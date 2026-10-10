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


def _walk(node, out, seen_urn):
    """在嵌套 JSON 里递归找帖子正文。

    LinkedIn 把页面数据塞在 <code> 标签的 HTML 注释里，结构很深且经常变，
    比起猜 HTML 类名，直接找 commentary 字段更抗改动。
    """
    if isinstance(node, dict):
        c = node.get("commentary")
        if isinstance(c, dict):
            t = c.get("text")
            text = ""
            if isinstance(t, dict):
                text = (t.get("text") or "").strip()
            elif isinstance(t, str):
                text = t.strip()
            urn = node.get("urn") or node.get("entityUrn") or ""
            if text and (not urn or urn not in seen_urn):
                if urn:
                    seen_urn.add(urn)
                out.append({
                    "text": text,
                    "permalink": node.get("permalink") or "",
                    "created": node.get("createdAt") or node.get("publishedAt") or 0,
                    "urn": urn,
                })
        for v in node.values():
            _walk(v, out, seen_urn)
    elif isinstance(node, list):
        for v in node:
            _walk(v, out, seen_urn)


def parse_posts(html):
    """从页面 HTML 里提取帖子，失败时退化到正则。"""
    posts, seen = [], set()

    # 途径 1：内嵌 JSON（结构最完整）
    for m in re.finditer(r"<!--(\{.*?\})-->", html, re.S):
        raw = m.group(1)
        if "commentary" not in raw and "urn:li:activity" not in raw:
            continue
        try:
            _walk(json.loads(raw), posts, seen)
        except Exception:
            continue

    # 途径 2：JSON 不在注释里，而是 <script type="application/json">
    if not posts:
        for m in re.finditer(r'<script[^>]*type="application/json"[^>]*>(.*?)</script>', html, re.S):
            if "commentary" not in m.group(1):
                continue
            try:
                _walk(json.loads(m.group(1)), posts, seen)
            except Exception:
                continue

    # 途径 3：正则抓 data-urn 附近的可见文本（最后的兜底）
    if not posts:
        for m in re.finditer(r'urn:li:activity:(\d+)', html):
            urn = m.group(1)
            if urn in seen:
                continue
            tail = html[m.end(): m.end() + 6000]
            seg = re.search(r'class="[^"]*update-components-text[^"]*"[^>]*>(.*?)</(?:div|span)>',
                            tail, re.S)
            text = re.sub(r"<[^>]+>", " ", seg.group(1)).strip() if seg else ""
            if len(text) < 10:
                continue
            seen.add(urn)
            posts.append({"text": re.sub(r"\s+", " ", text),
                          "permalink": "https://www.linkedin.com/feed/update/urn:li:activity:%s" % urn,
                          "created": 0, "urn": urn})
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

    cutoff_ms = int((datetime.now(CST) - timedelta(days=args.days)).timestamp() * 1000)
    items = []
    for p in posts:
        created = int(p.get("created") or 0)
        if created and created < cutoff_ms:
            continue
        text = re.sub(r"\s+", " ", p["text"]).strip()
        if len(text) < 10:
            continue
        # 帖子没有标题，用正文首行做标题
        first = text.split("\n")[0].strip()
        title = first if len(first) <= 90 else first[:90] + "…"
        dt = (datetime.fromtimestamp(created / 1000, CST) if created
              else datetime.now(CST))
        items.append({
            "topic": TOPIC,
            "cat": "官方",
            "title": title,
            "summary": text[:600],
            "source": SOURCE,
            "url": p.get("permalink") or "",
            "pubDate": dt.strftime("%Y-%m-%d"),
        })

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
