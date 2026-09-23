#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日新闻汇总台 —— YouTube Temu 视频抓取 + 总结脚本（YouTube Data API v3）

做什么：
    1. 搜索过去 48 小时内发布的、标题/描述含 "Temu" 的视频
       （全球各语种，不限语言/地区；两路搜索：order=viewCount 保热门 + order=date 保最新）
    2. 拉取视频详情（播放 / 点赞 / 评论数 / 时长 / 描述）
    3. 拉取每个视频的热门评论（relevance 排序 top 20）
    4. 规则式总结 —— 全部基于真实数据，不编造：
       - 内容摘要 = 视频描述摘录（去链接/推广行）+ 章节列表
       - 评论区小结 = 情绪比例（英/西语词典分类）+ 高频主题词统计
       - 热门评论 = 点赞最高的 5 条
    5. 任意语言自动检测译成中文（sl=auto，品牌名占位符保护，失败保留原文）

API 消耗：搜索 2 次（200 units）+ 详情 1 次 + 评论每视频 1 次 ≈ 210 units/天
（免费额度 10000 units/天，绰绰有余）

用法：
    python3 fetch_youtube.py                # 抓取 → 写 inbox/youtube-日期.json → 更新 index.html
    python3 fetch_youtube.py --hours 48     # 搜索时间窗（默认 48 小时）
    python3 fetch_youtube.py --max 8        # 最多保留 N 个视频（默认 8）
    python3 fetch_youtube.py --min-duration 60   # 过滤短于 N 秒的视频（默认 60，滤掉 shorts）
    python3 fetch_youtube.py --no-update    # 只生成 JSON，不改动页面
    python3 fetch_youtube.py --print        # 把结果打到标准输出，方便核对

未配置 YOUTUBE_API_KEY 时优雅跳过（exit 0），不影响 workflow 里的其他步骤。
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
INBOX = os.path.join(ROOT, "inbox")
CST = timezone(timedelta(hours=8))
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

API_BASE = "https://www.googleapis.com/youtube/v3/"

# ---- 品牌占位符保护复用 fetch_news（Temu/Shein/Amazon 等不被音译坏） ----
try:
    sys.path.insert(0, HERE)
    from fetch_news import _protect, _restore  # noqa: E402
except Exception as _ex:  # fetch_news 改名/损坏时不至于全挂
    sys.stderr.write("[WARN] 无法导入 fetch_news 品牌保护（%s），改用无占位符兜底\n" % _ex)

    def _protect(text):
        return text, {}

    def _restore(text, slots):
        return text

# ---- 字幕抓取（可选依赖：pip install youtube-transcript-api） ----
# 缺库或被 YouTube 拦截时，内容总结自动降级为描述摘录，管道不断。
try:
    from youtube_transcript_api import YouTubeTranscriptApi as _YTTA  # noqa: E402
except Exception:
    _YTTA = None


# ---------------------------------------------------------------------------
# 多语言翻译：全球视频（英/西/葡/捷/阿/日/韩…）→ 中文
# Google gtx 端点 sl=auto 自动检测源语言；失败保留原文（卡片始终有原视频链接）。
# ---------------------------------------------------------------------------
def _gtx_auto(text):
    url = "https://translate.googleapis.com/translate_a/single?" + urllib.parse.urlencode(
        {"client": "gtx", "sl": "auto", "tl": "zh-CN", "dt": "t", "q": text})
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    raw = urllib.request.urlopen(req, timeout=25).read().decode("utf-8")
    return "".join(seg[0] for seg in json.loads(raw)[0] if seg and seg[0])


def needs_translation(text):
    """判断文本是否需要送翻译。
    - 含日文假名/韩文谚文 → 不是中文，翻
    - 无 CJK 汉字 → 翻（英/西/捷/阿等）
    - 含汉字：≥2 个汉字且汉字多于拉丁字母 → 视为中英混合/中文，豁免；
      否则翻（比如只有一个汉字的泰文/纯品牌标题）
    """
    if not text or not text.strip():
        return False
    if re.search(r"[\u3040-\u30ff\uac00-\ud7af]", text):
        return True
    cjk = re.findall(r"[\u4e00-\u9fff]", text)
    if not cjk:
        return True
    latin = len(re.findall(r"[A-Za-z]", text))
    return not (len(cjk) >= 2 and latin < len(cjk))


def translate_any(text, cache):
    if not needs_translation(text):
        return text, False
    if text in cache:
        return cache[text], True
    guarded, slots = _protect(text)
    try:
        out = (_gtx_auto(guarded) or "").strip()
        if out and out != guarded:
            out = _restore(out, slots) if slots else out
            if out:
                cache[text] = out
                return out, True
    except Exception:
        pass
    return text, False


def log(msg):
    print(msg, flush=True)


# ---------------------------------------------------------------------------
# 情绪词典：只做分类统计，不猜测语义。先匹配多词短语，再匹配单词。
# ---------------------------------------------------------------------------
NEG_PHRASES = [
    "cheap quality", "cheaply made", "poor quality", "bad quality", "fell apart",
    "never again", "rip off", "ripoff", "not worth", "not recommended", "waste of money",
    "waste of time", "do not buy", "don't buy", "got scammed", "got a refund",
    "going back", "returned mine", "sending it back", "throws away",
    # 西语
    "no funciona", "dinero perdido", "no lo compro", "me arrepiento",
]
POS_PHRASES = [
    "worth it", "worth every", "highly recommend", "so cute", "love it", "loved it",
    "best ever", "pretty good", "really good", "surprisingly good", "great quality",
    "good quality", "amazing quality", "works great", "held up", "no regrets",
    # 西语
    "me gusta", "me encanta", "muy bueno", "muy buena",
]

NEG_WORDS = {
    "scam", "scams", "scammer", "scammers", "trash", "garbage", "terrible", "awful",
    "worst", "hate", "hated", "hates", "broke", "broken", "refund", "refunds",
    "returned", "return", "waste", "disappointed", "disappointing", "avoid",
    "warning", "lawsuit", "fake", "counterfeit", "nasty", "stolen", "boycott",
    "danger", "dangerous", "unsafe", "toxic", "banned", "illegal", "dropshipper",
    "dropshipping", "cheaply", "shoddy", "flimsy", "falling apart", "useless",
    # 西语
    "estafa", "estafas", "malo", "mala", "malos", "malas", "horrible", "pesimo",
    "basura", "roto", "rompe", "rompio", "falso", "falsa", "peligro", "peligroso",
}
POS_WORDS = {
    "love", "loved", "lovely", "great", "good", "best", "awesome", "amazing",
    "cute", "adorable", "perfect", "recommend", "recommended", "happy", "nice",
    "excellent", "worth", "affordable", "deal", "deals", "bargain", "obsessed",
    "stunning", "favorite", "favourite", "beautiful", "funny", "hilarious",
    "wholesome", "helpful", "thanks", "thank", "genius", "underrated",
    "satisfying", "impressive", "legit", "solid", " impressed",
    # 西语
    "encanta", "increible", "genial", "bueno", "buena", "buenos", "buenas",
    "bonito", "bonita", "barato", "barata", "perfecto", "gracias",
    "hermoso", "hermosa", "economico",
}


def _norm_latin(text):
    """去重音并只留 a-z 空格：increíble → increible。西语/葡语词典匹配的前提。"""
    t = unicodedata.normalize("NFD", (text or "").lower())
    t = "".join(ch for ch in t if unicodedata.category(ch) != "Mn")
    return " " + re.sub(r"[^a-z' ]", " ", t) + " "


def classify_sentiment(text):
    """返回 pos / neg / neu。短语优先于单词，负面短语优先于正面词（宁严勿宽）。
    词典覆盖英语 + 西语高频情绪词（Temu 内容两大语种）；其他语种归中性。"""
    t = _norm_latin(text)
    for p in NEG_PHRASES:
        if p in t:
            return "neg"
    for p in POS_PHRASES:
        if p in t:
            return "pos"
    words = set(t.split())
    if words & NEG_WORDS:
        return "neg"
    if words & POS_WORDS:
        return "pos"
    return "neu"


# ---------------------------------------------------------------------------
# 主题词典：英文关键词 → 中文标签。multi-word 在前，命中即计一次。
# 只统计真实出现的词，页面展示频次 top N。
# ---------------------------------------------------------------------------
THEMES = [
    (r"customer service", "客服"),
    (r"\bquality\b", "质量"),
    (r"\bprices?\b|\bpricing\b|\bcost\b", "价格"),
    (r"\bshipping\b|\bdelivery\b|\bdelivered\b|\bshipped\b", "物流"),
    (r"\bscams?\b|\bscammy\b", "骗局"),
    (r"\brefunds?\b|\breturn(ed|s)?\b", "退款退货"),
    (r"\bsiz(e|es|ing)\b", "尺码"),
    (r"\bfit(s|ted)?\b", "版型"),
    (r"\bclothes\b|\bclothing\b|\bshirts?\b|\bdress(es)?\b|\bhoodies?\b", "服装"),
    (r"\bmakeup\b|\bcosmetics\b", "美妆"),
    (r"\bnails?\b", "美甲"),
    (r"\bjewel(l)?ery\b", "饰品"),
    (r"\bkitchen\b|\bcookware\b", "厨具"),
    (r"\bhome (finds|decor|goods)\b|\bdecor\b", "家居"),
    (r"\bgadgets?\b|\btech finds\b", "数码小物"),
    (r"\bplants?\b", "植物"),
    (r"\bpet (stuff|supplies|toys)\b|\bdog (toys|stuff)\b|\bcat (toys|stuff)\b", "宠物用品"),
    (r"\bdupes?\b", "平替"),
    (r"\bunbox(ing)?\b|\bhauls?\b", "开箱"),
    (r"\breview(s|ed)?\b|\btesting\b", "评测"),
    (r"\brecommend(s|ed|ation)?\b", "推荐"),
    (r"\bpackaging\b", "包装"),
    (r"\baliexpress\b|\bshein\b|\bamazon\b", "其他平台对比"),
    # 西语（Temu 内容第二大语种）
    (r"\bcalidad\b", "质量"),
    (r"\bprecio(s)?\b", "价格"),
    (r"\benvio\b|\bentrega\b|\bpaquete\b", "物流"),
    (r"\bestafa(s)?\b", "骗局"),
    (r"\bdevolucion\b|\bdevolver\b", "退款退货"),
    (r"\bropa\b|\bcamisa\b|\bvestido\b", "服装"),
    (r"\bmaquillaje\b", "美妆"),
    (r"\bcocina\b", "厨具"),
    (r"\brecomend(o|a|ar)\b", "推荐"),
    (r"\bbarato\b|\bbarata\b", "便宜好物"),
]


def extract_themes(text):
    t = _norm_latin(text)      # 去重音：envío → envio，西语主题才匹配得上
    found = []
    for pat, cn in THEMES:
        n = len(re.findall(pat, t))
        if n:
            found.append((cn, n))
    # 合并同名主题计数
    agg = {}
    for cn, n in found:
        agg[cn] = agg.get(cn, 0) + n
    return sorted(agg.items(), key=lambda kv: -kv[1])


def parse_duration(iso):
    """PT12M34S → 秒。"""
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m:
        return 0
    h, mi, s = (int(x) if x else 0 for x in m.groups())
    return h * 3600 + mi * 60 + s


def fmt_duration(sec):
    if sec >= 3600:
        return "%d:%02d:%02d" % (sec // 3600, sec % 3600 // 60, sec % 60)
    return "%d:%02d" % (sec // 60, sec % 60)


def clean_description(desc, limit=320):
    """摘要 = 描述摘录：丢含链接的行（推广位常见「标签+URL 同行」）、#标签行、
    纯大写推广行，保留真实正文。"""
    lines = []
    used = 0
    for raw in (desc or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        low = line.lower()
        if "http" in low or low.startswith("www."):
            continue
        if re.match(r"^[#＃@]\S+$", line):
            continue
        if "subscribe" in low and len(line) < 60:
            continue
        if low.startswith(("follow me", "tiktok:", "instagram:", "business email", "sponsor")):
            continue
        if re.match(r"^\d{1,2}:\d{2}", line):     # 章节行单独提取
            continue
        lines.append(line)
        used += len(line) + 1
        if used >= limit:
            break
    text = " ".join(lines)
    if len(text) > limit:
        text = text[:limit].rstrip() + "…"
    return text


def extract_chapters(desc, max_n=6):
    """从描述里抽章节（00:00 Intro 这种）。"""
    out = []
    for m in re.finditer(r"(?:^|\n)\s*((?:\d{1,2}:)?\d{1,2}:\d{2})\s+[-–—~|]?\s*(.{2,60}?)(?=\s*$)",
                         desc or "", re.M):
        ts, name = m.group(1), m.group(2).strip()
        if re.fullmatch(r"[\W\s]+", name):        # 章节名全是符号就跳过
            continue
        out.append({"ts": ts, "name": name})
        if len(out) >= max_n:
            break
    return out


# ---------------------------------------------------------------------------
# 字幕全文 → 抽取式内容总结
# 原则：只从字幕里抽取真实说过的句子（带时间戳可回溯核对），不生成、不编造。
# ---------------------------------------------------------------------------
def _clean_caption(text):
    """去 [Music]/[Applause] 之类的标记和空白。"""
    t = (text or "").replace("\n", " ").strip()
    t = re.sub(r"[\[（(【]\s*(music|applause|laughter|音乐|掌声|笑)\s*[\]）)】]", " ", t, flags=re.I)
    t = re.sub(r"^\[.*?\]\s*", "", t).strip()
    return t


def _fetch_transcript_ytta(video_id):
    """youtube-transcript-api 直连。返回 [(start秒, 文本), ...]；失败返回 []。
    注：GitHub Actions 的数据中心 IP 常被 YouTube 拦截（本地家宽通常没问题）。"""
    if _YTTA is None:
        return []
    segs = []
    try:
        if hasattr(_YTTA, "list"):                      # v1.x：实例 API
            api = _YTTA()
            try:
                tr_list = list(api.list(video_id))
                # 优先手工字幕（更准确），否则用第一个（多为自动生成）
                tr = next((t for t in tr_list if not getattr(t, "is_generated", True)),
                          tr_list[0] if tr_list else None)
                if tr is None:
                    return []
                fetched = tr.fetch()
            except Exception:
                fetched = api.fetch(video_id)
            for s in fetched:
                segs.append((float(getattr(s, "start", 0.0) or 0.0),
                             getattr(s, "text", "") or ""))
        else:                                           # 旧版 0.x：静态方法
            for s in _YTTA.get_transcript(video_id):
                segs.append((float(s.get("start", 0.0) or 0.0),
                             s.get("text", "") or ""))
    except Exception as ex:
        log("        · [字幕] 直连失败（%s），尝试 Invidious 镜像…" % type(ex).__name__)
        return []
    cleaned = []
    for st, tx in segs:
        tx = _clean_caption(tx)
        if tx:
            cleaned.append((st, tx))
    return cleaned


# Invidious 公共镜像：直连被拦时的第二数据源。实例随时可能挂，轮询到能用为止。
INVIDIOUS_INSTANCES = [
    "https://inv.nadeko.net",
    "https://invidious.nerdvpn.de",
    "https://yewtu.be",
    "https://iv.melmac.space",
    "https://invidious.f5.si",
]


def _parse_webvtt(raw):
    """WebVTT → [(start秒, 文本), ...]。"""
    segs = []
    cur_start = None
    for line in raw.splitlines():
        line = line.strip()
        m = re.match(r"(\d{1,2}):(\d{2}):(\d{2})[.,]\d{3}\s*-->", line)
        if m:
            cur_start = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
            continue
        if not line or line.startswith(("WEBVTT", "Kind:", "Language:", "NOTE")) or "-->" in line:
            continue
        tx = _clean_caption(re.sub(r"<[^>]+>", "", line))
        if tx and cur_start is not None:
            segs.append((float(cur_start), tx))
    return segs


def _fetch_transcript_invidious(video_id):
    for base in INVIDIOUS_INSTANCES:
        try:
            req = urllib.request.Request(
                base + "/api/v1/captions/" + video_id,
                headers={"User-Agent": UA, "Accept": "application/json"})
            data = json.loads(urllib.request.urlopen(req, timeout=8).read().decode("utf-8"))
            caps = data.get("captions") or []
            if not caps:
                continue
            # 优先手工字幕（label 不含 auto-generated）
            caps.sort(key=lambda c: 1 if "auto" in (c.get("label") or "").lower() else 0)
            url = caps[0].get("url") or ""
            if url.startswith("/"):
                url = base + url
            raw = urllib.request.urlopen(
                urllib.request.Request(url, headers={"User-Agent": UA}),
                timeout=15).read().decode("utf-8", "ignore")
            segs = _parse_webvtt(raw)
            if segs:
                return segs
        except Exception:
            continue          # 实例挂了/超时，换下一个
    return []


def _fetch_transcript_ytdlp(video_id):
    """yt-dlp 用 ios/android client 抓字幕（与 watch 页面不同风控面）。
    未安装 yt-dlp 或失败返回 []。产物是 WebVTT 文件。"""
    if shutil.which("yt-dlp") is None:
        return []
    import glob
    import tempfile
    tmpd = tempfile.mkdtemp(prefix="ytsub-")
    try:
        r = subprocess.run(
            ["yt-dlp", "--skip-download", "--write-subs", "--write-auto-subs",
             "--sub-langs", ".*", "--sub-format", "vtt/best",
             "--extractor-args", "youtube:player_client=ios,android",
             "--no-warnings", "--quiet",
             "-o", os.path.join(tmpd, "%(id)s"),
             "https://www.youtube.com/watch?v=" + video_id],
            capture_output=True, timeout=60)
        vtts = glob.glob(os.path.join(tmpd, "*.vtt"))
        if not vtts:
            return []
        # 优先非 auto（手工）字幕：文件名带 .lang.vtt，手工的排在前面即可（按文件大小，手工一般更大更完整）
        vtts.sort(key=lambda p: (1 if ".auto." in os.path.basename(p) or os.path.basename(p).count(".") > 2 else 0,
                                 -os.path.getsize(p)))
        for p in vtts:
            segs = _parse_webvtt(open(p, encoding="utf-8", errors="ignore").read())
            if segs:
                return segs
        return []
    except Exception:
        return []
    finally:
        shutil.rmtree(tmpd, ignore_errors=True)


def _fetch_transcript_segs(video_id):
    """抓字幕原文段：直连 → Invidious 镜像 → yt-dlp(ios/android client)，
    全失败返回 []（调用方降级为描述摘录）。"""
    segs = _fetch_transcript_ytta(video_id)
    if segs:
        return segs
    segs = _fetch_transcript_invidious(video_id)
    if segs:
        return segs
    segs = _fetch_transcript_ytdlp(video_id)
    if not segs:
        log("        · [字幕] 三条路都没拿到，该视频降级为描述摘录")
    return segs


def _info_density(text):
    """实词密度：拉丁词/汉字越多越有信息量。"""
    words = re.findall(r"[A-Za-z\u00c0-\u024f\u0400-\u04ff\u4e00-\u9fff]+", text)
    return sum(len(w) for w in words)


def summarize_transcript(segs, max_points=5):
    """字幕全文 → 抽取式摘要：全程均分 N 个时间窗，每窗选信息密度最高的一句。
    返回 [{t: "mm:ss", s: 句子}, ...]（s 为字幕原文，由调用方翻译）。"""
    if not segs:
        return []
    # 合并成句单元：累积到 ~150 字符或遇到句末标点
    units = []
    buf, buf_start = "", None
    for st, tx in segs:
        if buf_start is None:
            buf_start = st
        buf = (buf + " " + tx).strip()
        if len(buf) >= 150 or (tx and tx[-1] in ".!?。！？"):
            if buf:
                units.append({"start": buf_start, "text": buf})
            buf, buf_start = "", None
    if buf:
        units.append({"start": buf_start, "text": buf})
    units = [u for u in units if len(u["text"]) >= 30]
    if not units:
        return []

    if len(units) <= max_points:
        picked = units
    else:
        span = len(units) / max_points
        picked = []
        for i in range(max_points):
            lo = int(i * span)
            hi = max(int((i + 1) * span), lo + 1)
            window = units[lo:hi]
            if window:
                picked.append(max(window, key=lambda u: _info_density(u["text"])))

    out = []
    for u in picked:
        sec = int(u["start"] or 0)
        out.append({"t": "%d:%02d" % (sec // 60, sec % 60),
                    "s": u["text"][:220].rstrip() + ("…" if len(u["text"]) > 220 else "")})
    return out


def build_transcript_summary(video_id, max_points=5):
    """抓字幕并生成抽取式摘要；失败返回 []（调用方降级为描述摘录）。"""
    return summarize_transcript(_fetch_transcript_segs(video_id), max_points=max_points)


# ---------------------------------------------------------------------------
# YouTube Data API v3
# ---------------------------------------------------------------------------
def api_get(path, params, key, timeout=25):
    params = dict(params)
    params["key"] = key
    url = API_BASE + path + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def search_video_ids(key, hours, per_search=50):
    """两路搜索（不限定语言/地区，全球 Temu 内容）：viewCount（热门优先）+ date（保最新）。"""
    after = (datetime.now(timezone.utc) - timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M:%SZ")
    ids = []
    for order in ("viewCount", "date"):
        try:
            data = api_get("search", {
                "part": "snippet", "q": "Temu", "type": "video",
                "order": order, "publishedAfter": after,
                "maxResults": per_search,
            }, key)
            for it in data.get("items", []):
                vid = (it.get("id") or {}).get("videoId")
                if vid and vid not in ids:
                    ids.append(vid)
        except Exception as ex:
            log("[SKIP] 搜索失败（order=%s）：%s" % (order, ex))
        time.sleep(0.4)
    return ids


def fetch_video_details(ids, key):
    """批量拉详情，返回 {videoId: {...}}。"""
    out = {}
    for i in range(0, len(ids), 50):
        chunk = ids[i:i + 50]
        try:
            data = api_get("videos", {
                "part": "snippet,statistics,contentDetails",
                "id": ",".join(chunk),
            }, key)
        except Exception as ex:
            log("[SKIP] 详情拉取失败：%s" % ex)
            continue
        for it in data.get("items", []):
            out[it["id"]] = {
                "snippet": it.get("snippet") or {},
                "statistics": it.get("statistics") or {},
                "contentDetails": it.get("contentDetails") or {},
            }
        time.sleep(0.3)
    return out


def fetch_comments(video_id, key, max_n=20):
    """拉热门评论（relevance 排序）。失败返回空列表。"""
    comments = []
    try:
        data = api_get("commentThreads", {
            "part": "snippet", "videoId": video_id,
            "maxResults": max_n, "order": "relevance", "textFormat": "plainText",
        }, key)
        for it in data.get("items", []):
            sn = (((it.get("snippet") or {}).get("topLevelComment") or {}).get("snippet") or {})
            # 评论里的推广链接是纯噪音，清掉再入库
            text = re.sub(r"https?://\S+", "", (sn.get("textDisplay") or "")).strip()
            if text:
                comments.append({"text": text, "likes": int(sn.get("likeCount") or 0)})
    except Exception:
        return []          # 评论关闭 / 被删 / API 抖动，都当没有评论处理
    return comments


def summarize_video(v, key, min_comments_for_stats=3):
    """单个视频的规则式总结。全部产出都是真实数据的摘录或统计，不做推测。
    内容总结优先用字幕全文抽取（带时间戳），无字幕/被拦时降级为描述摘录。"""
    sn = v["snippet"]
    stats = v["statistics"]
    desc = sn.get("description") or ""

    log("        · 抓字幕做内容总结…")
    summary_points = build_transcript_summary(v["videoId"])
    if summary_points:
        summary = ""
        summary_source = "transcript"
    else:
        summary = clean_description(desc)
        summary_source = "description"

    comments = fetch_comments(v["videoId"], key)
    sentiment = {"pos": 0, "neg": 0, "neu": 0}
    themes = {}
    for c in comments:
        s = classify_sentiment(c["text"])
        sentiment[s] += 1
        for cn, n in extract_themes(c["text"]):
            themes[cn] = themes.get(cn, 0) + n

    total = sum(sentiment.values())
    pct = {k: round(v * 100 / total) for k, v in sentiment.items()} if total else {"pos": 0, "neg": 0, "neu": 0}

    # 情绪条：中性灰色、正面绿、负面红（统计事实，不是编造）
    top_themes = sorted(themes.items(), key=lambda kv: -kv[1])[:4]

    if total >= min_comments_for_stats:
        if pct["pos"] >= pct["neg"] + 20:
            mood = "整体偏正面"
        elif pct["neg"] >= pct["pos"] + 20:
            mood = "整体偏负面"
        elif pct["pos"] < 15 and pct["neg"] < 15:
            mood = "整体中性"
        else:
            mood = "正负掺半"
        parts = ["热门评论%s：%d%% 表达正面、%d%% 表达负面" % (mood, pct["pos"], pct["neg"])]
        if top_themes:
            parts.append("讨论最多的是 " + "、".join(
                "%s（%d 次）" % (cn, n) for cn, n in top_themes[:2]))
        comment_summary = "；".join(parts) + "。"
    elif comments:
        comment_summary = "评论较少（仅 %d 条），不足以给出可靠的倾向统计。" % len(comments)
    else:
        comment_summary = "该视频评论区不可用（已关闭或无评论）。"

    # 热门评论：点赞排序取前 5，太短的丢掉（没信息量）
    hot = sorted(comments, key=lambda c: -c["likes"])[:5]
    hot = [dict(c, sent=classify_sentiment(c["text"]))
           for c in hot if len(c["text"]) >= 12][:5]

    return {
        "videoId": v["videoId"],
        "title": (sn.get("title") or "").strip(),
        "channel": (sn.get("channelTitle") or "").strip(),
        "publishedAt": (sn.get("publishedAt") or "")[:10],
        "durationSec": parse_duration(v["contentDetails"].get("duration")),
        "views": int(stats.get("viewCount") or 0),
        "likes": int(stats.get("likeCount") or 0),
        "commentCount": int(stats.get("commentCount") or 0),
        "summary": summary,
        "summarySource": summary_source,
        "summaryPoints": summary_points,
        "chapters": extract_chapters(desc),
        "sentiment": pct,
        "sampled": total,
        "themes": [{"name": cn, "count": n} for cn, n in top_themes],
        "commentSummary": comment_summary,
        "topComments": hot,
    }


def load_api_key():
    """key 来源：环境变量 YOUTUBE_API_KEY > 项目根 .env.local（不进 git，本地跑用）。"""
    key = os.environ.get("YOUTUBE_API_KEY", "").strip()
    if key:
        return key
    env_file = os.path.join(ROOT, ".env.local")
    if os.path.isfile(env_file):
        try:
            for line in open(env_file, encoding="utf-8"):
                line = line.strip()
                if line.startswith("YOUTUBE_API_KEY="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
        except Exception:
            pass
    return ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hours", type=int, default=48, help="搜索时间窗（小时）")
    ap.add_argument("--max", type=int, default=8, help="最多保留多少个视频")
    ap.add_argument("--min-duration", type=int, default=60, help="过滤短于 N 秒的视频")
    ap.add_argument("--no-update", action="store_true", help="只生成 JSON，不更新页面")
    ap.add_argument("--no-translate", action="store_true", help="跳过中文翻译")
    ap.add_argument("--print", dest="do_print", action="store_true", help="打印结果 JSON")
    args = ap.parse_args()

    key = load_api_key()
    if not key:
        log("[SKIP] 未配置 YOUTUBE_API_KEY（环境变量或项目根 .env.local），本次跳过")
        return

    now = datetime.now(CST)
    log("    [1/5] 搜索过去 %d 小时的 Temu 视频…" % args.hours)
    ids = search_video_ids(key, args.hours)
    if not ids:
        log("[FAIL] YouTube 搜索没有返回任何结果（API 配额或网络问题？）")
        sys.exit(1)
    log("        搜到 %d 个候选" % len(ids))

    log("    [2/5] 拉取视频详情…")
    details = fetch_video_details(ids, key)
    cands = []
    for vid, d in details.items():
        dur = parse_duration(d["contentDetails"].get("duration"))
        title = (d["snippet"].get("title") or "")
        descr = (d["snippet"].get("description") or "")
        if dur < args.min_duration:
            continue
        if "temu" not in (title + " " + descr).lower():
            continue
        cands.append(dict(d, videoId=vid, _dur=dur))
    cands.sort(key=lambda v: -int(v["statistics"].get("viewCount") or 0))
    cands = cands[:args.max]
    if not cands:
        log("[FAIL] 时间窗内没有符合条件的 Temu 视频，页面保持原样")
        sys.exit(1)
    log("        选取 %d 个（按播放量）" % len(cands))

    log("    [3/5] 抓取热门评论并做情绪/主题统计…")
    videos = []
    for i, v in enumerate(cands, 1):
        log("        (%d/%d) %s" % (i, len(cands), v["snippet"].get("title", "")[:60]))
        videos.append(summarize_video(v, key))
        time.sleep(0.3)

    if not args.no_translate:
        log("    [4/5] 翻译成中文（自动检测源语言 + 品牌名占位符保护）…")
        cache = {}
        for v in videos:
            t, _ = translate_any(v["title"], cache)
            v["titleOriginal"] = v["title"]
            v["title"] = t
            s, _ = translate_any(v["summary"], cache)
            v["summary"] = s
            for p in v.get("summaryPoints") or []:
                p["s"], _ = translate_any(p["s"], cache)
            for ch in v["chapters"]:
                ch["name"], _ = translate_any(ch["name"], cache)
            for c in v["topComments"]:
                c["text"], _ = translate_any(c["text"], cache)
            time.sleep(0.1)
        log("        翻译完成，失败条目保留原文")
    else:
        log("    [4/5] 已按 --no-translate 跳过翻译")
        for v in videos:
            v["titleOriginal"] = v["title"]

    out = {"updatedAt": now.strftime("%Y-%m-%dT%H:%M"), "videos": videos}
    os.makedirs(INBOX, exist_ok=True)
    path = os.path.join(INBOX, "youtube-%s.json" % now.strftime("%Y-%m-%d"))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    log("\n[OK] 已写入 %s（%d 个视频）" % (path, len(videos)))

    if args.do_print:
        print(json.dumps(out, ensure_ascii=False, indent=2))

    if args.no_update:
        return

    r = subprocess.run([sys.executable, os.path.join(HERE, "update_youtube.py"), "--file", path],
                       cwd=HERE)
    if r.returncode != 0:
        log("[FAIL] update_youtube.py 执行失败")
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
