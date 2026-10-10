#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抓取 LinkedIn 公司页面的最新帖子，合并进新闻汇总台。

为什么必须要 cookie：
    未登录时，公司主页只能拿到粉丝数这类指标，帖子字段一个都没有
    （feed-shared-update / actorName 出现 0 次）；帖子页直接 302 到登录页。
    RSSHub 的 LinkedIn 路由需要自托管配 cookie，官方实例一律 403。
    搜索引擎也不索引 LinkedIn 帖子（Bing site: 限定查询 0 条）。
    所以要拿帖子，只能带登录态请求。

环境变量：
    LI_AT   LinkedIn 登录 cookie 的值。未设置时脚本跳过，不影响主流程。

获取方式（建议在浏览器无痕窗口里操作）：
    1. 登录 linkedin.com
    2. F12 打开开发者工具 → Application（应用）→ Storage → Cookies → https://www.linkedin.com
    3. 找到名为 li_at 的那一行，复制它的 Value
    4. 存到 GitHub Secrets：
       gh secret set LI_AT --repo <用户名>/<仓库名> --body "<复制的值>"

注意：cookie 会过期（几个月到一年不等），过期后抓取会拿不到帖子，
脚本会明确报「登录态失效」，重新按上面步骤取一次即可。

用法：
    python3 scripts/fetch_linkedin.py                  # 抓最近 3 天，写入 index.html
    python3 scripts/fetch_linkedin.py --days 7 --max 5
    python3 scripts/fetch_linkedin.py --no-update      # 只生成 JSON，不改页面
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
INBOX = os.path.join(ROOT, "inbox")
CST = timezone(timedelta(hours=8))
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# 公司 LinkedIn 主页。换成别的公司只改这里。
COMPANY = os.environ.get("LI_COMPANY", "temuapp")
# 归入哪个话题。页面目前只有 ubisoft / temu 两个板块。
TOPIC = os.environ.get("LI_TOPIC", "temu")
SOURCE = "LinkedIn"


def log(msg):
    print(msg, flush=True)


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """不自动跟随重定向。

    LinkedIn 对无效 cookie 的处理是 302 到登录页，让 urllib 自动跟随会在
    登录页之间绕圈，最后只报一句「infinite loop」，看不出真正原因。
    这里改成手动判断跳转目标，给出「cookie 失效」这种能直接动手修的提示。
    """
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch(li_at):
    url = "https://www.linkedin.com/company/%s/posts/?feedView=all" % COMPANY
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Cookie": "li_at=%s" % li_at,
    })
    opener = urllib.request.build_opener(_NoRedirect)
    try:
        with opener.open(req, timeout=30) as r:
            raw = r.read()
    except urllib.error.HTTPError as e:
        if e.code in (301, 302, 303, 307, 308):
            loc = (e.headers.get("Location") or "")
            setc = (e.headers.get("Set-Cookie") or "")
            # LinkedIn 认出无效 cookie 时有两个特征信号：
            #   1) 回一个 li_at=delete me（1970 过期），主动把 cookie 作废
            #   2) 302 的目标就是原地址，形成自重定向
            # 命中任一即可判定登录态失效。
            if "delete me" in setc or loc.rstrip("/") == url.rstrip("/"):
                raise RuntimeError("登录态失效：LinkedIn 拒绝了 li_at cookie"
                                   "（响应带回 li_at=delete me），请重新取一次")
            if any(k in loc.lower() for k in ("authwall", "login", "/uas/", "signin")):
                raise RuntimeError("登录态失效：被重定向到登录页，li_at cookie 已过期")
            with opener.open(urllib.request.Request(
                    loc, headers={"User-Agent": UA,
                                  "Cookie": "li_at=%s" % li_at}), timeout=30) as r2:
                raw = r2.read()
        else:
            raise
    if isinstance(raw, bytes) and raw[:2] == b"\x1f\x8b":
        import gzip
        raw = gzip.decompress(raw)
    return raw.decode("utf-8", "ignore")


def is_login_wall(html):
    """未登录或 cookie 失效时，LinkedIn 会返回一个登录页。"""
    m = re.search(r"<title>(.*?)</title>", html, re.S)
    title = (m.group(1).strip() if m else "").lower()
    return ("sign in" in title or "log in" in title or "authwall" in html.lower())


def _unescape(html):
    """把 RSC 载荷里的转义还原，方便直接用正则匹配。

    页面把整棵 React 组件树当成 JS 字符串塞进 <script>，里面的引号是 \\" ，
    换行是 \\n。先还原成正常 JSON 文本，后面才好按结构取字段。
    """
    return html.replace('\\"', '"').replace('\\n', '\n').replace('\\\\', '\\')


# 正文在 RSC 树里有三种形态，都在 commentary 组件内部：
#   1) {"children":[null,"一句话"]}                      普通段落
#   2) {"children":[["$","br",null,{}],"一句话"]}         换行后的段落
#   3) [null,"前半句",[...span 链接...]]                  句子中间夹了 @提及/话题标签
#      （结尾也可能是 ,null]，两种都要认）
#   4) {"children":["ICQRF"]}                            被加粗/链出去的公司名
# 四种都要抓，否则会丢掉帖子第一句或中间的机构名。
_TEXT_PATS = [
    re.compile(r'\{"children":\[(?:null,|\["\$","br",null,\{\}\],)"((?:[^"\\]|\\.)*)"\]'),
    re.compile(r'\[null,"((?:[^"\\]|\\.)*)",(?:\[|null\])'),
    re.compile(r'\["\$","[^"]*",null,\{[^{}]{0,400}\}\],"((?:[^"\\]|\\.)*)"'),
    re.compile(r'\{"children":\["((?:[^"\\]|\\.){2,80})"\]\}'),
]
_CSS = re.compile(r'^[a-z0-9]+(?: [a-z0-9]+)*$')   # gflfb3 gfllgi 这类样式名，不是正文


def _block_text(seg):
    """从一个 commentary 区块里按出现顺序拼出正文。"""
    found = []
    for pat in _TEXT_PATS:
        for m in pat.finditer(seg):
            found.append((m.start(), m.group(1)))
    found.sort()
    lines, seen = [], set()
    for _, s in found:
        s = s.strip()
        if len(s) < 2 or s.startswith("$") or _CSS.match(s):
            continue
        # 正文里链出去的短网址（https://lnkd.in/xxx）不算正文，丢掉
        if s.startswith("http") and " " not in s:
            continue
        # 同一条帖子会连续渲染两遍，撞上第一句说明开始重复了，直接收尾
        if lines and s == lines[0]:
            break
        if s in seen:
            continue
        seen.add(s)
        lines.append(s)
    return _join(lines)


def _join(lines):
    """把切片拼回自然段落。

    被加粗链出去的机构名（Startup Valencia / ICQRF）在 RSC 里是独立节点，
    直接换行会变成「...with Spain's \n Startup Valencia \n , a private...」，
    所以按前后标点决定是接排还是换行。
    """
    buf = ""
    for s in lines:
        if not buf:
            buf = s
        elif buf[-1] in "([（“" or s[0] in ",.;:!?)]}）”'’":
            buf += s
        elif len(s) < 60 and buf[-1] not in ".!?…":
            buf += " " + s
        else:
            buf += "\n" + s
    return buf


def _rel_to_days(rel):
    """'3h' / '2d' / '1w' / '2mo' -> 天数（小数）。"""
    m = re.match(r'^(\d+)(m|h|d|w|mo|y)$', rel.strip())
    if not m:
        return None
    n, unit = int(m.group(1)), m.group(2)
    return {"m": n / 1440.0, "h": n / 24.0, "d": float(n),
            "w": n * 7.0, "mo": n * 30.0, "y": n * 365.0}[unit]


def _slug_words(url):
    """把帖子 slug URL 还原成词序列，用来和正文配对。

    https://.../temu-has-signed-of-a-memorandum-of-understanding-share-7513...-pnq
    -> ['temu','has','signed','of','a','memorandum','of','understanding']
    """
    tail = url.rstrip("/").split("/")[-1]
    tail = re.sub(r'-share-\d+.*$', '', tail)
    tail = re.sub(r'-\d{15,}.*$', '', tail)
    return [w for w in re.split(r'[^a-z0-9]+', tail.lower()) if w]


def _prefix_hit(slug_words, text_words):
    """slug 是正文前几个词生成的，比对前缀长度即可判定归属。"""
    n = 0
    for a, b in zip(slug_words, text_words):
        if a != b:
            break
        n += 1
    return n


def parse_posts(html):
    """解析 LinkedIn 新版 SDUI/RSC 页面里的公司帖子。

    页面已经不再输出 feed-shared-update-v2 那套 DOM，正文藏在内嵌 RSC 树中，
    靠 viewName=feed-commentary 定位帖子正文块，viewName=feed-full-update
    定位帖子起始（发布时间就在它后面），postSlugUrl 拿永久链接。
    """
    t = _unescape(html)

    # 1) 正文块：同一个帖子会被渲染两次（间隔 1~3k 字符），合并成一组
    groups = []
    for m in re.finditer(r'"viewName":"feed-commentary"', t):
        p = m.start()
        if groups and p - groups[-1][-1] < 6000:
            groups[-1].append(p)
        else:
            groups.append([p])

    # 2) 帖子起始位置（每个后面紧跟发布时间）
    starts = [m.start() for m in re.finditer(r'"viewName":"feed-full-update"', t)]
    times = {}
    for s in starts:
        m = re.search(r'"children":\["(\d+[mhdw]|(?:\d+)?mo|\d+y)"\]', t[s:s + 8000])
        times[s] = m.group(1) if m else ""

    # 3) 永久链接
    urls = [m.group(1) for m in
            re.finditer(r'postSlugUrl":"(https://www\.linkedin\.com/posts/[^"]+)"', t)]

    posts = []
    for i, g in enumerate(groups):
        # 正文可能跨到下一个 commentary 标记之后，给足窗口；但不能越过下一条帖子
        end = g[0] + 20000
        if i + 1 < len(groups):
            end = min(end, groups[i + 1][0])
        text = _block_text(t[g[0]:end])
        if len(text) < 10:
            continue
        # 发布时间：取本块之前最近的一个帖子起始点
        prev = [s for s in starts if s <= g[0]]
        rel = times.get(prev[-1], "") if prev else ""
        posts.append({"text": text, "rel": rel, "url": ""})

    # 4) 正文 ↔ 链接配对：slug 由正文前几个词生成，按前缀匹配度贪心分配
    if urls:
        tw = [[w for w in re.split(r'[^a-z0-9]+', p["text"].lower()) if w] for p in posts]
        pairs = []
        for i, p in enumerate(posts):
            for u in urls:
                pairs.append((_prefix_hit(_slug_words(u), tw[i]), i, u))
        pairs.sort(key=lambda x: -x[0])
        used_p, used_u = set(), set()
        for score, i, u in pairs:
            if score < 2 or i in used_p or u in used_u:
                continue
            posts[i]["url"] = u
            used_p.add(i)
            used_u.add(u)
    return posts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=3, help="只保留最近 N 天的帖子，默认 3")
    ap.add_argument("--max", type=int, default=6, help="最多保留 N 条，默认 6")
    ap.add_argument("--no-update", action="store_true", help="只生成 JSON，不改页面")
    args = ap.parse_args()

    li_at = (os.environ.get("LI_AT") or "").strip()
    if not li_at:
        log("  未设置 LI_AT，跳过 LinkedIn 抓取（需要先登录才能看到帖子）")
        return

    log("  抓取 LinkedIn @%s 的帖子…" % COMPANY)
    try:
        html = fetch(li_at)
    except Exception as ex:
        log("  [FAIL] 请求失败：%s" % str(ex)[:150])
        sys.exit(1)

    if is_login_wall(html):
        log("  [FAIL] 登录态失效：LinkedIn 返回的是登录页，li_at cookie 可能已过期，重新取一次")
        sys.exit(1)

    posts = parse_posts(html)
    if not posts:
        log("  [WARN] 页面拿到了但解析出 0 条帖子 —— LinkedIn 可能改了页面结构，需要更新解析规则")
        sys.exit(1)

    now = datetime.now(CST)
    items = []
    for p in posts:
        # 正文按行拼，去掉空行；标题用首行
        text = "\n".join(ln.strip() for ln in p["text"].split("\n") if ln.strip())
        if len(text) < 10:
            continue
        days = _rel_to_days(p.get("rel") or "")
        if days is not None and days > args.days:
            continue
        dt = now - timedelta(days=days) if days is not None else now
        flat = re.sub(r"\s+", " ", text)
        items.append({
            "topic": TOPIC,
            "cat": "官方",
            "title": flat if len(flat) <= 90 else flat[:90] + "…",
            "summary": flat[:600],
            "source": SOURCE,
            "url": p.get("url") or "https://www.linkedin.com/company/%s/posts/" % COMPANY,
            "pubDate": dt.strftime("%Y-%m-%d"),
        })

    # 官方帖子是英文，和新闻一样译成中文再上页面
    try:
        from fetch_news import translate
        items = translate(items)
    except Exception as ex:
        log("  [WARN] 翻译未生效（%s），保留英文原文" % str(ex)[:80])

    items = items[: args.max]
    log("  解析到 %d 条，保留最近 %d 天内的 %d 条" % (len(posts), args.days, len(items)))

    out = {"date": datetime.now(CST).strftime("%Y-%m-%d"), "items": items}
    os.makedirs(INBOX, exist_ok=True)
    path = os.path.join(INBOX, "linkedin-%s.json" % out["date"])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    log("  [OK] 已写入 %s" % path)
    for it in items:
        log("    [%s] %s" % (it["pubDate"], it["title"][:56]))

    if args.no_update or not items:
        return

    r = subprocess.run([sys.executable, os.path.join(HERE, "update_news.py"), "--file", path],
                       cwd=ROOT)
    if r.returncode != 0:
        log("[FAIL] update_news.py 执行失败")
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
