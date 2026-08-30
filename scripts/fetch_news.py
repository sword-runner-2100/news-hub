#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日新闻汇总台（云端版）—— 新闻抓取脚本

双源策略，各取所长：

  1) Google News RSS（主源，保数量与时效）
     https://news.google.com/rss/search?q=<query>+when:3d&hl=...&gl=...&ceid=...
     - 支持 when:3d 语法精准过滤最近 3 天，单个话题能返回 20-60 条，时效性极好
     - 提供 <source> 标签，来源名准确
     - 缺点：链接是加密的 protobuf 中转地址（news.google.com/rss/articles/CBMi...），
       无法解析成原文直链，但浏览器点击会自动跳转到原文
     - 缺点：没有正文摘要

  2) Bing News RSS（补充源，保质量）
     https://www.bing.com/news/search?q=<query>&format=RSS&setmkt=en-US
     - description 是正文前几句的真实摘要，不需要 AI 编造
     - 链接是标准 302 中转，跟随重定向即可拿到原文直链
     - 缺点：只支持英文市场（setmkt=zh-CN 时返回 HTML 而非 RSS），且条目少

合并时 Bing 的条目优先（有摘要、有直链），Google 的补充数量。
英文条目保留原文，中文条目直接采用 Google 中文源的中文标题 —— 不依赖任何 AI 翻译
（GitHub Models 已按计划退役，服务端返回 410，详见 translate() 注释）。

用法：
    python3 scripts/fetch_news.py                  # 抓最近 3 天，写入 index.html
    python3 scripts/fetch_news.py --days 2         # 抓最近 2 天
    python3 scripts/fetch_news.py --max 8          # 每个话题最多保留 8 条
    python3 scripts/fetch_news.py --no-update      # 只生成 JSON，不改页面
    python3 scripts/fetch_news.py --no-translate   # 跳过中文翻译

环境变量：
    GITHUB_TOKEN   可选。有则翻译，无则保留英文。GitHub Actions 里自动注入。
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
INBOX = os.path.join(ROOT, "inbox")
CST = timezone(timedelta(hours=8))
UTC = timezone.utc
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# (话题, 搜索词, hl, gl, ceid) —— Google 用 when:Nd 过滤。
# 中英文各一路：中文源直接给中文标题，英文源覆盖面更广、抓到后翻译成中文。
GOOGLE_QUERIES = [
    ("ubisoft", "育碧", "zh-CN", "CN", "CN:zh-Hans"),
    ("ubisoft", "Ubisoft", "en-US", "US", "US:en"),
    ("ubisoft", "Ubisoft Assassin's Creed Rainbow Six", "en-US", "US", "US:en"),
    ("ubisoft", "Ubisoft earnings stock studio", "en-US", "US", "US:en"),
    ("temu", "Temu", "zh-CN", "CN", "CN:zh-Hans"),
    ("temu", "Temu", "en-US", "US", "US:en"),
    ("temu", "Temu PDD Holdings earnings", "en-US", "US", "US:en"),
    ("temu", "Temu EU regulation tariff customs", "en-US", "US", "US:en"),
]
# Bing 只支持英文市场，但它的摘要是正文原文片段 —— 英文源的主力就靠它
BING_QUERIES = [
    ("ubisoft", "Ubisoft"),
    ("ubisoft", "Ubisoft Assassin's Creed"),
    ("ubisoft", "Ubisoft Rainbow Six Far Cry"),
    ("temu", "Temu"),
    ("temu", "Temu PDD Holdings"),
    ("temu", "Temu EU regulation tariff"),
    ("temu", "Temu Shein cross-border ecommerce"),
]

# 博彩 / SEO 垃圾站常用词。这类站点会把广告词塞进新闻标题混进 Google News，
# 命中即丢弃，避免污染页面。
JUNK_WORDS = [
    "威尼斯", "AG网上", "网上注册", "网上娱乐", "真人", "利来", "龙8", "23300",
    "博彩", "赌博", "赌场", "老虎机", "彩票", "开户", "注册送", "首存", "流水",
    "官方网址", "官网登录", "登录首页", "下载app", "最新网址", "备用网址",
    "娱乐平台", "棋牌", "捕鱼", "一元购", "提现", "返水", "代理加盟",
]
# 已知的低质 / 敏感来源，整源屏蔽
JUNK_SOURCES = [
    "风闻", "womenofchina", "大纪元", "新唐人", "ntdtv", "epoctimes",
    "shenyun", "神韵", "renminbao", "人民报",
]
# 正规媒体优先（同分时排在前面）
TRUSTED = [
    "reuters", "bloomberg", "ft.com", "wsj", "cnbc", "forbes", "the verge",
    "engadget", "ign", "gamespot", "polygon", "eurogamer", "pcgamer", "heise",
    "techcrunch", "scmp", "straitstimes", "nikkei", "yahoo", "investing.com",
    "thepaper", "澎湃", "凤凰", "新浪", "界面", "36氪", "虎嗅", "经济观察",
    "第一财经", "财新", "亿邦动力", "雨果网", "亿恩网", "联合早报", "香港01",
    "ubisoft", "prnewswire", "businesswire", "globenewswire",
]

CATS = [
    ("财报", ["revenue", "profit", "earnings", "quarter", "q1 ", "q2 ", "q3 ", "q4 ",
             "results", "guidance", "营收", "财报", "净利", "季度"]),
    ("监管", ["eu ", "european", "regulation", "regulator", "fine", "penalty", "tariff", "dsa",
             "lawsuit", "court", "ban", "compliance", "antitrust", "customs", "罚款", "监管", "上诉", "诉讼"]),
    ("资本市场", ["stock", "shares", "analyst", "rating", "price target", "investor",
                 "valuation", "upgrade", "downgrade", "股价", "评级", "目标价"]),
    ("战略", ["strategy", "expand", "expansion", "supply chain", "local", "warehouse",
             "logistics", "partnership", "invest", "restructur", "战略", "供应链", "本地仓"]),
    ("产品", ["game", "launch", "release", "update", "season", "remake", "dlc", "patch",
             "beta", "announce", "游戏", "发售", "上线", "更新", "赛季"]),
]


def log(msg):
    print(msg, flush=True)


def http_get(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def parse_date(s):
    if not s:
        return None
    try:
        return parsedate_to_datetime(s).astimezone(UTC)
    except Exception:
        return None


# ---------------- Google News ----------------
def fetch_google(topic, query, hl, gl, ceid, days):
    q = "%s when:%dd" % (query, days)
    url = "https://news.google.com/rss/search?" + urllib.parse.urlencode(
        {"q": q, "hl": hl, "gl": gl, "ceid": ceid})
    try:
        root = ET.fromstring(http_get(url))
    except Exception as ex:
        log("    [SKIP] Google 抓取失败 %s: %s" % (query, str(ex)[:60]))
        return []
    out = []
    for it in root.findall(".//item"):
        title = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        src_el = it.find("source")
        source = (src_el.text or "").strip() if src_el is not None else ""
        if not title or not link:
            continue
        # Google 标题形如 "正文 - 来源名"，去掉尾巴
        if source and title.endswith(" - " + source):
            title = title[: -(len(source) + 3)].strip()
        out.append({"topic": topic, "title": title, "url": link, "summary": "",
                    "source": source, "pub": parse_date(it.findtext("pubDate") or ""),
                    "直链": False})
    return out


# ---------------- Bing News ----------------
def fetch_bing(topic, query):
    url = "https://www.bing.com/news/search?" + urllib.parse.urlencode(
        {"q": query, "format": "RSS", "count": "25", "setmkt": "en-US", "setlang": "en-US"})
    try:
        root = ET.fromstring(http_get(url))
    except Exception as ex:
        log("    [SKIP] Bing 抓取失败 %s: %s" % (query, str(ex)[:60]))
        return []
    out = []
    for it in root.findall(".//item"):
        title = (it.findtext("title") or "").strip()
        link = (it.findtext("link") or "").strip()
        if not title or not link:
            continue
        desc = re.sub(r"<[^>]+>", " ", it.findtext("description") or "")
        desc = re.sub(r"\s+", " ", desc).strip()
        out.append({"topic": topic, "title": title, "url": link, "summary": desc[:400],
                    "source": "Bing News", "pub": parse_date(it.findtext("pubDate") or ""),
                    "直链": False})
    return out


def resolve_real_url(link, timeout=15):
    """跟随 Bing 的 302 中转，拿到真实原文地址；Google 的中转无法解析，原样返回。"""
    if "bing.com/news/apiclick" not in link:
        return link
    try:
        req = urllib.request.Request(link, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            real = r.geturl()
            return real if real and real.startswith("http") else link
    except Exception:
        return link


def norm(t):
    """标题归一化，用于跨源去重。"""
    s = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", "", t.lower())
    return s[:70]


def guess_cat(text):
    low = text.lower()
    for name, keys in CATS:
        for k in keys:
            if k in low:
                return name
    return "其他"


def is_junk(x):
    """过滤博彩垃圾标题、低质来源，以及被 SEO 标签塞满的标题。"""
    src = (x.get("source") or "").lower()
    for bad in JUNK_SOURCES:
        if bad.lower() in src:
            return True
    title = x.get("title") or ""
    for w in JUNK_WORDS:
        if w.lower() in title.lower():
            return True
    # 标题里出现两组以上竖线分隔，通常是 SEO 标签堆砌
    if title.count("|") >= 2:
        return True
    # 个人频道 / 聚合站的噪声条目，如 "senorablitz's Library"、"electrostreet's Library"
    if re.search(r"\b\w+'s\s+Library\b", title, re.I):
        return True
    return False


def is_chinese(s):
    """中文字符占比达到三成就认为是中文条目（用于排序）。"""
    if not s:
        return False
    cn = len(re.findall(r"[\u4e00-\u9fff]", s))
    return cn / max(1, len(s)) >= 0.3


def has_cn(s, n=3):
    """是否含足够多的中文字符（用于判断要不要送去翻译）。

    比 is_chinese 宽松：像「Ubisoft正式确认Rainbow Six自己的XCOM」这种中英混合标题，
    中文占比不到三成但其实不用翻，硬翻反而会被翻译接口弄坏。
    """
    return len(re.findall(r"[\u4e00-\u9fff]", s or "")) >= n


def trust_score(x, prefer_cn=False):
    """排序打分：有摘要 > 正规媒体 > 时间；prefer_cn 时中文标题额外 +200。

    prefer_cn 只在「关闭翻译」时才开 —— 那时英文条目读不了，只能靠中文源保可读性。
    开启翻译后所有条目最终都会变成中文，再偏袒原生中文反而会把英文源挤掉，故关掉。
    """
    src = (x.get("source") or "").lower()
    s = 0
    if prefer_cn and is_chinese(x.get("title")):
        s += 200
    if x.get("summary"):
        s += 100
    for t in TRUSTED:
        if t in src:
            s += 50
            break
    if "bing" in src:
        s += 10
    return s


def _gtx(text):
    """Google 翻译的公开 gtx 端点，质量最好。"""
    url = "https://translate.googleapis.com/translate_a/single?" + urllib.parse.urlencode(
        {"client": "gtx", "sl": "en", "tl": "zh-CN", "dt": "t", "q": text})
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    raw = urllib.request.urlopen(req, timeout=25).read().decode("utf-8")
    return "".join(seg[0] for seg in json.loads(raw)[0] if seg and seg[0])


def _mymemory(text):
    """MyMemory 免费翻译，作为备用。"""
    url = "https://api.mymemory.translated.net/get?" + urllib.parse.urlencode(
        {"q": text, "langpair": "en|zh-CN"})
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    d = json.loads(urllib.request.urlopen(req, timeout=25).read().decode("utf-8"))
    return ((d.get("responseData") or {}).get("translatedText") or "").strip()


# 品牌 / 产品 / 公司名：翻译前抽成占位符，翻译后原样还原。
# 不这么做的话 Temu 会被音译成「特姆」「特木」，PDD 也被拆得面目全非。
BRANDS = [
    "PDD Holdings", "PDD", "Temu", "Shein", "AliExpress", "TikTok Shop",
    "Ubisoft", "Ubisoft+", "Assassin's Creed", "Rainbow Six Siege", "Rainbow Six",
    "Far Cry", "Heroes of Might and Magic", "Might and Magic", "Skull and Bones",
    "The Division", "Tom Clancy's", "Just Dance", "For Honor", "Anno",
    "Steam", "SteamDB", "SteamCharts", "Snowdrop", "PlayStation", "Xbox",
    "Nintendo", "Epic Games", "Gamescom", "E3", "Tencent", "Amazon", "Walmart",
    "DSA", "VLOP", "IPO", "CEO", "CFO",
]


def _protect(text):
    """把品牌名换成占位符，返回 (处理后文本, 占位符→原文 映射)。"""
    slots = {}
    out = text
    for b in BRANDS:
        def rep(m):
            key = "QX%dQX" % len(slots)
            slots[key] = m.group(0)
            return key
        out = re.sub(re.escape(b), rep, out, flags=re.I)
    return out, slots


def _restore(text, slots):
    for k, v in slots.items():
        text = text.replace(k, v)
    # 兜底：万一占位符被翻译 API 拆开，把残留的 QX..QX 清掉
    return re.sub(r"QX\s*\d+\s*QX", "", text).strip()


def translate_one(text, cache):
    """把一段英文译成中文。已是中文或翻译失败则原样返回。"""
    if not text or not text.strip():
        return text, False
    if has_cn(text):
        return text, False
    if text in cache:
        return cache[text], True

    guarded, slots = _protect(text)
    for fn in (_gtx, _mymemory):
        try:
            out = (fn(guarded) or "").strip()
            if out and out != guarded:
                out = _restore(out, slots) if slots else out
                if out:
                    cache[text] = out
                    return out, True
        except Exception:
            continue
    return text, False


def translate(items):
    """把英文标题与摘要译成中文。

    背景：原本打算用 GitHub Models（models.github.ai/inference），但它已在按计划退役，
    服务端返回 410 github_models_retirement_brownout；官方的 actions/ai-inference
    也改成只支持 Copilot，需要用户自备 COPILOT_PAT。

    因此改用免费翻译接口：Google 公开翻译端点为主、MyMemory 为备。
    翻译只做语言转换，不增删改任何事实；原文链接始终保留，可点开核对。
    """
    cache = {}
    n_t = n_d = n_fail = 0
    for it in items:
        t, ok1 = translate_one(it.get("title", ""), cache)
        if ok1:
            n_t += 1
        elif not has_cn(it.get("title", "")):
            n_fail += 1
        it["title"] = t

        if it.get("summary"):
            d, ok2 = translate_one(it["summary"], cache)
            if ok2:
                n_d += 1
            it["summary"] = d
        time.sleep(0.12)          # 轻微限速，避免被判滥用

    log("    [OK] 翻译完成：标题 %d 条、摘要 %d 条%s"
        % (n_t, n_d, ("，%d 条失败保留英文" % n_fail) if n_fail else ""))
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=3, help="Google 源只保留最近 N 天，默认 3")
    ap.add_argument("--bing-days", type=int, default=7,
                    help="Bing 源时间窗更宽（它带真实摘要但更新慢），默认 7 天")
    ap.add_argument("--max", type=int, default=8, help="每个话题最多保留 N 条，默认 8")
    ap.add_argument("--no-update", action="store_true", help="只生成 JSON，不改页面")
    ap.add_argument("--no-translate", action="store_true",
                    help="关闭中文翻译（默认开启，走免费翻译接口）")
    args = ap.parse_args()

    now = datetime.now(UTC)
    cutoff = now - timedelta(days=args.days)

    log("  抓取 Google News RSS（最近 %d 天）…" % args.days)
    google_all = []
    for topic, q, hl, gl, ceid in GOOGLE_QUERIES:
        got = fetch_google(topic, q, hl, gl, ceid, args.days)
        log("    %-22s → %d 条" % (q, len(got)))
        google_all.extend(got)

    log("  抓取 Bing News RSS（补充摘要与直链）…")
    bing_all = []
    for topic, q in BING_QUERIES:
        got = fetch_bing(topic, q)
        log("    %-22s → %d 条" % (q, len(got)))
        bing_all.extend(got)

    # Bing 的新闻日期普遍偏旧，给它更宽的时间窗，换取带摘要的高质量条目
    bing_cutoff = now - timedelta(days=args.bing_days)

    # Bing 优先（有摘要、可解析直链），Google 补充数量；全程过滤垃圾
    merged, seen, junked = [], set(), 0
    for pool, lim in ((bing_all, bing_cutoff), (google_all, cutoff)):
        for x in pool:
            if x["pub"] and x["pub"] < lim:
                continue
            if is_junk(x):
                junked += 1
                continue
            k = norm(x["title"])
            if not k or k in seen:
                continue
            seen.add(k)
            merged.append(x)

    if not merged:
        log("\n[FAIL] 没抓到任何近期新闻，页面保持原样")
        sys.exit(1)

    # 排序：有摘要 + 正规媒体优先，其次按时间。
    # 只有在「关闭翻译」时才额外偏袒原生中文（否则英文条目最后也会译成中文，不该被挤掉）
    prefer_cn = args.no_translate
    merged.sort(key=lambda x: (trust_score(x, prefer_cn), x["pub"] or now), reverse=True)

    n_bing = sum(1 for x in merged if "bing" in (x["source"] or "").lower())
    log("\n  去重后 %d 条（Bing 系 %d / 其余 %d），过滤垃圾 %d 条" %
        (len(merged), n_bing, len(merged) - n_bing, junked))

    # 解析 Bing 的真实直链
    need = [x for x in merged if "bing.com/news/apiclick" in x["url"]]
    if need:
        log("  解析原文直链（%d 条）…" % len(need))
        with ThreadPoolExecutor(max_workers=6) as ex:
            reals = list(ex.map(resolve_real_url, [x["url"] for x in need]))
        for x, real in zip(need, reals):
            x["url"] = real
            x["直链"] = real != x["url"] or True
        log("    完成 %d 条" % len(need))

    # 每话题限量（merged 已按可信度+时间排好序，直接取前 N 条）
    final = []
    for topic in ("ubisoft", "temu"):
        rows = [x for x in merged if x["topic"] == topic]
        final.extend(rows[: args.max])

    items = []
    for x in final:
        blob = (x["title"] + " " + x["summary"]).strip()
        items.append({
            "topic": x["topic"],
            "cat": guess_cat(blob),
            "title": x["title"][:200],
            "summary": x["summary"][:600],
            "source": x["source"][:60] or "—",
            "url": x["url"],
            "pubDate": x["pub"].strftime("%Y-%m-%d") if x["pub"] else "",
        })

    if args.no_translate:
        log("    [提示] 已按 --no-translate 关闭翻译，英文条目保留原文")
    else:
        items = translate(items)

    out = {"date": datetime.now(CST).strftime("%Y-%m-%d"), "items": items}
    os.makedirs(INBOX, exist_ok=True)
    path = os.path.join(INBOX, "news-%s.json" % out["date"])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    log("\n[OK] 已写入 %s" % path)
    for it in items:
        flag = "摘" if it["summary"] else "  "
        lang = "中" if has_cn(it["title"]) else "英"
        log("    [%s][%s][%-7s][%s] %s" % (flag, lang, it["topic"], it["cat"], it["title"][:56]))

    if args.no_update:
        return

    r = subprocess.run([sys.executable, os.path.join(HERE, "update_news.py"), "--file", path], cwd=ROOT)
    if r.returncode != 0:
        log("[FAIL] update_news.py 执行失败")
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
