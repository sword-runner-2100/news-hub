#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把本次新抓到的新闻推送到企业微信群机器人。

用法：
    python3 scripts/push_wechat.py                 # 推送 inbox/added.json 里的新增条目
    python3 scripts/push_wechat.py --dry-run       # 只打印要发的消息，不真的发

环境变量：
    WECHAT_WEBHOOK   企业微信群机器人的 Webhook 地址（存到 GitHub Secrets）。
                     未设置时脚本静默跳过，不报错 —— 方便先跑通抓取再配推送。

为什么选企业微信群机器人：
    免费、无需认证、无需服务器，群里加一个机器人就能拿到一个 webhook 地址，
    从 GitHub Actions 直接 POST 即可。个人微信没有官方的对外推送接口。

企业微信的限制（已在代码里处理）：
    - markdown 消息正文上限 4096 字节（中文约 1300 字），超了要截断
    - 支持的语法有限：# 标题、**加粗**、[链接](url)、> 引用、
      <font color="info|comment|warning"> 着色；不支持表格和图片
"""

import argparse
import json
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ADDED_PATH = os.path.join(ROOT, "inbox", "added.json")
HTML_PATH = os.path.join(ROOT, "index.html")

TOPIC_CN = {"ubisoft": "育碧", "temu": "Temu"}
# 企业微信 markdown 正文上限，留一点余量
MAX_BYTES = 3800


def log(msg):
    print(msg, flush=True)


def load_added():
    if not os.path.isfile(ADDED_PATH):
        log("  没有找到 inbox/added.json，跳过推送")
        return None
    with open(ADDED_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_steam():
    """从 index.html 里读 Steam 在线人数，附在消息末尾。"""
    try:
        html = open(HTML_PATH, encoding="utf-8").read()
        blk = html.split("/* <<<STEAM_DATA_START>>> */")[1].split("/* <<<STEAM_DATA_END>>> */")[0]
        return json.loads(re.search(r"const\s+STEAM_DATA\s*=\s*(\{.*\});", blk, re.S).group(1))
    except Exception:
        return None


def build_content(payload, steam):
    items = payload.get("items") or []
    date = payload.get("date") or ""
    md = date[5:] if len(date) >= 10 else date   # 2026-09-04 → 09-04

    by_topic = {}
    for it in items:
        by_topic.setdefault(it.get("topic", ""), []).append(it)

    lines = ["# 新闻早报 · %s" % md, "今日新增 %d 条" % len(items), ""]

    for topic in ("ubisoft", "temu"):
        rows = by_topic.get(topic) or []
        if not rows:
            continue
        lines.append("**%s**（%d 条）" % (TOPIC_CN.get(topic, topic), len(rows)))
        for it in rows:
            title = (it.get("title") or "").strip()
            url = (it.get("url") or "").strip()
            summary = (it.get("summary") or "").strip()
            source = (it.get("source") or "").strip()
            cat = (it.get("cat") or "").strip()

            head = "[**%s**](%s)" % (title, url) if url else "**%s**" % title
            lines.append("> %s" % head)
            if summary:
                # 摘要过长会挤掉后面的条目，截到 70 字
                s = summary if len(summary) <= 70 else summary[:70] + "…"
                lines.append("> %s" % s)
            meta = " · ".join([x for x in (source, cat) if x])
            if meta:
                lines.append('> <font color="comment">%s</font>' % meta)
            lines.append("")
        lines.append("")

    if steam and steam.get("games"):
        parts = ["%s %s" % (g["nameCn"], format(g["current"], ",")) for g in steam["games"]]
        lines.append('<font color="comment">Steam 在线：%s</font>' % " / ".join(parts))
        lines.append("")

    content = "\n".join(lines).strip()

    # 超长截断：按整条丢弃，避免把一条新闻截成半句
    while len(content.encode("utf-8")) > MAX_BYTES:
        cut = content.rfind("> <font color=")
        if cut <= 0:
            break
        content = content[:cut].rstrip()
        if not content.endswith("…"):
            content += "\n\n<font color=\"comment\">…内容过长，已截断，完整版见网页</font>"
    return content


def send(webhook, content):
    body = json.dumps({"msgtype": "markdown", "markdown": {"content": content}}).encode("utf-8")
    req = urllib.request.Request(
        webhook, data=body,
        headers={"Content-Type": "application/json", "User-Agent": "news-hub-bot"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="只打印消息内容，不发送")
    args = ap.parse_args()

    webhook = (os.environ.get("WECHAT_WEBHOOK") or "").strip()
    if not webhook and not args.dry_run:
        log("  未设置 WECHAT_WEBHOOK，跳过推送（把它存到仓库 Secrets 后即可生效）")
        return

    payload = load_added()
    if not payload:
        return
    items = payload.get("items") or []
    if not items:
        log("  本次没有新增条目，跳过推送")
        return

    content = build_content(payload, load_steam())
    size = len(content.encode("utf-8"))

    if args.dry_run:
        print("\n--- 将要发送的消息（%d 字节）---\n" % size)
        print(content)
        print("\n--- 结束 ---")
        return

    log("  推送 %d 条新闻（%d 字节）…" % (len(items), size))
    try:
        res = send(webhook, content)
    except Exception as ex:
        log("[FAIL] 推送失败：%s" % str(ex)[:200])
        sys.exit(1)

    if res.get("errcode") == 0:
        log("  [OK] 推送成功")
    else:
        log("[FAIL] 企业微信返回错误：errcode=%s errmsg=%s"
            % (res.get("errcode"), res.get("errmsg")))
        sys.exit(1)


if __name__ == "__main__":
    main()
