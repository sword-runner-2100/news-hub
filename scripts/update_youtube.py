#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日新闻汇总台 —— YouTube 视频数据合并进 index.html

用法：
    python3 update_youtube.py --file inbox/youtube-2026-09-23.json

输入 JSON 格式（由 fetch_youtube.py 产出）：
{
  "updatedAt": "2026-09-23T09:00",
  "videos": [ { "videoId": "...", "title": "...", ... } ]
}

合并策略：
    - 新视频 fetchedAt = 抓取日，页面上出现在当天的分组块里（像新闻时间线按天一块）
    - 在榜视频：数据字段（播放/评论等）持续更新，但保留首次上榜日，分组位置不挪窝
    - 只保留 fetchedAt 在近 RETAIN_DAYS 天内的，最多 MAX_VIDEOS 条
    - 数据没变化就不改动文件（幂等）
    - 每次改动前自动备份 index.html 到 backups/（保留最近 10 份）
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
HTML_PATH = os.path.join(ROOT, "index.html")
BACKUP_DIR = os.path.join(ROOT, "backups")
START_MARK = "/* <<<YOUTUBE_DATA_START>>> */"
END_MARK = "/* <<<YOUTUBE_DATA_END>>> */"
CST = timezone(timedelta(hours=8))
RETAIN_DAYS = 10        # 旧视频保留窗口：首次上榜日算起的自然日数
MAX_VIDEOS = 96         # 页面最多展示的视频数（每天最多 8 个新上榜 × 10 天窗口）


def die(msg):
    print("[FAIL] " + msg, file=sys.stderr)
    sys.exit(1)


def backup():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    stamp = datetime.now(CST).strftime("%Y%m%d-%H%M%S")
    dst = os.path.join(BACKUP_DIR, "index-%s.html" % stamp)
    shutil.copy2(HTML_PATH, dst)
    olds = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith("index-") and f.endswith(".html")])
    for f in olds[:-10]:
        try:
            os.remove(os.path.join(BACKUP_DIR, f))
        except OSError:
            pass
    return dst


def balanced_object(src, name):
    """从 JS 源码里按花括号配平取出 `const name = {...}` 的对象字面量，返回 (start, end)。"""
    p = src.find(name)
    if p < 0:
        die("找不到 %s" % name)
    i = src.find("{", p)
    if i < 0:
        die("%s 后面没有找到 {" % name)
    depth = 0
    for k in range(i, len(src)):
        if src[k] == "{":
            depth += 1
        elif src[k] == "}":
            depth -= 1
            if depth == 0:
                return i, k + 1
    die("%s 的花括号不配平" % name)


def eval_js_object(lit):
    """把 JS 对象字面量（键未加引号）安全地转成 Python 对象。"""
    return json.loads(_quote_keys(lit))


def _quote_keys(lit):
    out = []
    n = len(lit)
    k = 0
    in_str = False
    quote = ""
    while k < n:
        ch = lit[k]
        if in_str:
            out.append(ch)
            if ch == "\\" and k + 1 < n:
                out.append(ch_next(lit, k))
                k += 2
                continue
            if ch == quote:
                in_str = False
            k += 1
            continue
        if ch in ('"', "'"):
            in_str = True
            quote = ch
            out.append(ch)
            k += 1
            continue
        if ch.isalpha() or ch == "_":
            m = k
            while m < n and (lit[m].isalnum() or lit[m] in "_"):
                m += 1
            word = lit[k:m]
            p = m
            while p < n and lit[p] in " \t\r\n":
                p += 1
            if p < n and lit[p] == ":":
                out.append('"%s"' % word)
            else:
                out.append(word)
            k = m
            continue
        out.append(ch)
        k += 1
    return "".join(out)


def ch_next(lit, k):
    return lit[k + 1] if k + 1 < len(lit) else ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True, help="待导入的 YouTube 数据 JSON 路径")
    ap.add_argument("--no-backup", action="store_true", help="不做备份")
    args = ap.parse_args()

    src = args.file if os.path.isabs(args.file) else os.path.join(os.getcwd(), args.file)
    if not os.path.isfile(src):
        die("找不到输入文件：%s" % src)
    try:
        with open(src, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except Exception as ex:
        die("输入文件解析失败：%s" % ex)

    incoming = payload.get("videos")
    if not isinstance(incoming, list) or not incoming:
        die("JSON 里没有 videos 数组")

    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    s = html.find(START_MARK)
    e = html.find(END_MARK)
    if s < 0 or e < 0:
        die("index.html 里找不到 YOUTUBE_DATA 标记")

    block = html[s + len(START_MARK):e]
    i, j = balanced_object(block, "YOUTUBE_DATA")
    try:
        data = eval_js_object(block[i:j])
    except Exception as ex:
        die("YOUTUBE_DATA 解析失败：%s" % ex)

    old = {v.get("videoId"): v for v in data.get("videos", []) if v.get("videoId")}
    today = datetime.now(CST).strftime("%Y-%m-%d")
    cutoff = (datetime.now(CST) - timedelta(days=RETAIN_DAYS)).strftime("%Y-%m-%d")

    changed = []
    for nv in incoming:
        vid = nv.get("videoId")
        if not vid:
            continue
        ov = old.get(vid)
        if ov is None:
            # 新上榜视频：以今天作为它的分组日（页面上出现在今天的块里）
            nv["fetchedAt"] = today
            changed.append(vid)
        else:
            # 在榜视频：数据字段取最新，但保留首次上榜日，页面上不挪窝
            nv["fetchedAt"] = ov.get("fetchedAt") or today
            # 字幕总结是稀缺增强：新一轮没抓到字幕（description）时，
            # 保留已有的字幕版总结（transcript），不让低级来源覆盖高级来源
            if (nv.get("summarySource") != "transcript"
                    and ov.get("summarySource") == "transcript"
                    and ov.get("summaryPoints")):
                nv["summarySource"] = "transcript"
                nv["summaryPoints"] = ov["summaryPoints"]
                nv["summary"] = ov.get("summary", "")
            nv_first = ov.get("fetchedAt")
            nv_new = dict(nv)
            if json.dumps(ov, sort_keys=True, ensure_ascii=False) != \
               json.dumps(nv_new, sort_keys=True, ensure_ascii=False):
                changed.append(vid)
        old[vid] = nv

    # 只保留近期抓到的视频，控制页面体积
    merged = [v for v in old.values() if (v.get("fetchedAt") or "") >= cutoff]
    merged.sort(key=lambda v: (v.get("fetchedAt") or "", v.get("views") or 0), reverse=True)
    merged = merged[:MAX_VIDEOS]

    if not changed and json.dumps(data.get("videos", []), sort_keys=True, ensure_ascii=False) == \
                       json.dumps(merged, sort_keys=True, ensure_ascii=False):
        print("[OK] 没有检测到变化，页面未改动")
        return

    data["videos"] = merged
    data["updatedAt"] = str(payload.get("updatedAt") or
                            datetime.now(CST).strftime("%Y-%m-%dT%H:%M"))

    if not args.no_backup:
        backup()

    body = json.dumps(data, ensure_ascii=False, indent=2)
    new_block = (START_MARK + "\nconst YOUTUBE_DATA = " + body + ";\n" + END_MARK)
    new_html = html[:s] + new_block + html[e + len(END_MARK):]
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(new_html)

    print("[OK] YouTube 数据已更新（%s）：%d 个视频在页面上（新增/更新 %d 个）"
          % (data["updatedAt"], len(merged), len(changed)))


if __name__ == "__main__":
    main()
