#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日新闻汇总台 —— Steam 在线人数数据更新脚本

用法：
    python3 update_steam.py --file inbox/steam-2026-08-30.json

输入 JSON 格式：
{
  "updatedAt": "2026-08-30T09:00",          # 可选，缺省取当前时间
  "games": [
    {
      "appId": "2507950",                    # 必填，用来定位是哪个游戏
      "current": 78862,                      # 当前在线
      "peak24h": 112831,                     # 24 小时峰值
      "allTimePeak": 247028,                 # 历史峰值
      "allTimePeakDate": "2025-09",          # 历史峰值日期（月度点，精确到月）
      "daily": [                             # 可选；给了就整段替换，不给就只更新上面的实时数字
        {"date":"2026-08-23","peak":112632,"avg":64956,"n":24},
        {"date":"2026-08-29","peak":82661,"avg":62360,"n":12}
      ]
    }
  ]
}

说明：
    - daily 数组按日期升序；peak=当日峰值、avg=当日均值、n=当日采样次数
    - 最后一天通常采样不完整（当天还没过完），页面会把末段画成虚线
    - 只传需要更新的游戏即可，未提及的游戏保持原样
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
START_MARK = "/* <<<STEAM_DATA_START>>> */"
END_MARK = "/* <<<STEAM_DATA_END>>> */"
CST = timezone(timedelta(hours=8))
LIVE_FIELDS = ("current", "peak24h", "allTimePeak", "allTimePeakDate")
SERIES_FIELDS = ("daily", "monthly")


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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True, help="待导入的 Steam 数据 JSON 路径")
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

    incoming = payload.get("games") if isinstance(payload, dict) else None
    if not incoming:
        die("JSON 里没有 games 数组")

    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    s = html.find(START_MARK)
    e = html.find(END_MARK)
    if s < 0 or e < 0:
        die("index.html 里找不到 STEAM_DATA 标记")

    block = html[s + len(START_MARK):e]
    i, j = balanced_object(block, "STEAM_DATA")
    try:
        data = json.loads(json.dumps(eval_js_object(block[i:j])))
    except Exception as ex:
        die("STEAM_DATA 解析失败：%s" % ex)

    by_id = {str(g.get("appId")): g for g in data.get("games", [])}
    changed = []
    for ing in incoming:
        aid = str(ing.get("appId") or "").strip()
        if not aid:
            continue
        g = by_id.get(aid)
        if not g:
            print("     跳过：页面里没有 AppID %s" % aid)
            continue
        touched = []
        for f in LIVE_FIELDS:
            if ing.get(f) is not None:
                old = g.get(f)
                if old != ing[f]:
                    g[f] = ing[f]
                    touched.append("%s %s→%s" % (f, old, ing[f]))
        for fld in SERIES_FIELDS:
            rows = ing.get(fld)
            if isinstance(rows, list) and rows:
                if g.get(fld) != rows:
                    g[fld] = rows
                    touched.append("%s %d 天" % ("日度序列" if fld == "daily" else "月度表", len(rows)))
        if touched:
            changed.append((g.get("abbr") or aid, touched))

    if not changed:
        print("[OK] 没有检测到变化，页面未改动")
        return

    data["updatedAt"] = str(payload.get("updatedAt") or datetime.now(CST).strftime("%Y-%m-%dT%H:%M"))

    if not args.no_backup:
        backup()

    body = json.dumps(data, ensure_ascii=False, indent=2)
    new_block = START_MARK + "\nconst STEAM_DATA = " + body + ";\n" + END_MARK
    new_html = html[:s] + new_block + html[e + len(END_MARK):]
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(new_html)

    print("[OK] Steam 数据已更新（%s）" % data["updatedAt"])
    for abbr, touched in changed:
        print("     %s：%s" % (abbr, "；".join(touched)))


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
                out.append(lit[k + 1])
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
            # 只有后面紧跟冒号（允许空白）才当作键
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


if __name__ == "__main__":
    main()
