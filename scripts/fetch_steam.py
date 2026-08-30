#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日新闻汇总台 —— Steam 在线人数抓取脚本（直连 SteamCharts 数据端点）

数据源：https://steamcharts.com/app/<appId>/chart-data.json
该端点返回 [[毫秒时间戳, 在线人数], ...]，前面是月度点，后面逐步细化为小时级采样。
用它而不是解析 HTML 页面的原因：结构化、稳定、能拿到日粒度数据。

用法：
    python3 fetch_steam.py                      # 抓取 → 写 inbox/steam-日期.json → 自动更新 index.html
    python3 fetch_steam.py --days 14            # 抓取过去 14 天（默认 7）
    python3 fetch_steam.py --no-update          # 只生成 JSON，不改动页面
    python3 fetch_steam.py --print              # 把结果打到标准输出，方便核对

产出字段：
    current          最后一个采样点的在线人数
    peak24h          最近 24 小时内的峰值
    allTimePeak      全量数据里的最大值
    allTimePeakDate  峰值所在月份（数据为月度点，只能精确到月，格式 YYYY-MM）
    daily            [{date, peak, avg, n}, ...] 按日期升序，peak=当日峰值，avg=当日均值，n=当日采样次数
"""

import argparse
import json
import os
import subprocess
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
INBOX = os.path.join(ROOT, "inbox")
CST = timezone(timedelta(hours=8))
UTC = timezone.utc
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

APPS = [
    {"appId": "2507950", "name": "Delta Force", "nameCn": "三角洲行动", "abbr": "DF",
     "dev": "Team Jade / TiMi Studio Group"},
    {"appId": "2073620", "name": "Arena Breakout: Infinite", "nameCn": "暗区突围：无限", "abbr": "ABI",
     "dev": "Morefun Studios"},
]
ENDPOINT = "https://steamcharts.com/app/{appId}/chart-data.json"


def fetch(app_id, timeout=25):
    url = ENDPOINT.format(appId=app_id)
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def summarize(app, series, days):
    if not series:
        return None
    last_ts = series[-1][0]
    last_dt = datetime.fromtimestamp(last_ts / 1000, UTC)

    cur = series[-1][1]
    peak24h = max(v for ts, v in series if ts >= last_ts - 86400000)
    ap_ts, ap_val = max(series, key=lambda x: x[1])
    ap_month = datetime.fromtimestamp(ap_ts / 1000, UTC).strftime("%Y-%m")

    end_day = last_dt.date()
    start_day = end_day - timedelta(days=days - 1)
    buckets = {}
    for ts, v in series:
        d = datetime.fromtimestamp(ts / 1000, UTC).date()
        if start_day <= d <= end_day:
            buckets.setdefault(d, []).append(v)

    daily = []
    for d in sorted(buckets):
        vals = buckets[d]
        daily.append({"date": str(d), "peak": max(vals),
                      "avg": round(sum(vals) / len(vals)), "n": len(vals)})

    return {k: app[k] for k in ("appId", "name", "nameCn", "abbr", "dev")} | {
        "current": cur,
        "peak24h": peak24h,
        "allTimePeak": ap_val,
        "allTimePeakDate": ap_month,
        "daily": daily,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7, help="抓取过去 N 天，默认 7")
    ap.add_argument("--no-update", action="store_true", help="只生成 JSON，不更新 index.html")
    ap.add_argument("--print", dest="do_print", action="store_true", help="结果打到标准输出")
    args = ap.parse_args()

    now = datetime.now(CST)
    out = {"updatedAt": now.strftime("%Y-%m-%dT%H:%M"), "window": "过去 %d 天" % args.days, "games": []}
    failed = []

    for app in APPS:
        try:
            series = fetch(app["appId"])
            info = summarize(app, series, args.days)
        except Exception as ex:
            failed.append((app["abbr"], str(ex)))
            continue
        if not info or not info["daily"]:
            failed.append((app["abbr"], "数据为空"))
            continue
        out["games"].append(info)
        print("[OK] %-4s %-12s 当前=%-7d 24h峰=%-7d 史高=%-7d@%s  %d 天 (%s → %s)"
              % (info["abbr"], info["nameCn"], info["current"], info["peak24h"],
                 info["allTimePeak"], info["allTimePeakDate"], len(info["daily"]),
                 info["daily"][0]["date"], info["daily"][-1]["date"]))

    for abbr, err in failed:
        print("[SKIP] %s 抓取失败：%s" % (abbr, err))

    if not out["games"]:
        print("[FAIL] 两个游戏都没抓到，页面保持原样")
        sys.exit(1)

    os.makedirs(INBOX, exist_ok=True)
    path = os.path.join(INBOX, "steam-%s.json" % now.strftime("%Y-%m-%d"))
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print("\n[OK] 已写入 %s" % path)

    if args.do_print:
        print(json.dumps(out, ensure_ascii=False, indent=2))

    if args.no_update:
        return

    r = subprocess.run([sys.executable, os.path.join(HERE, "update_steam.py"), "--file", path],
                       cwd=HERE)
    if r.returncode != 0:
        print("[FAIL] update_steam.py 执行失败")
        sys.exit(r.returncode)


if __name__ == "__main__":
    main()
