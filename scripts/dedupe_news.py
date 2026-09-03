#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新闻去重 / 清理脚本（幂等，可重复运行）

背景：
    早期只按 url 去重，而 Google 源的链接是加密中转地址（news.google.com/rss/articles/CBMi...），
    同一篇文章换个关键词或市场抓回来 url 就变了。结果同一事件反复入库 ——
    实测「Ubisoft 出售了一款游戏，但忘记包含文字游戏部分」重复 4 次，
    全站 168 条里有 48 条是近似重复。

    修复后（fetch_news.py 译后去重 + update_news.py 标题去重）新数据不会再重复，
    但存量数据得单独洗一遍，这就是本脚本的作用。

保留策略（同一去重键下留哪条）：
    有摘要 > 来源可信 > 日期新 > 标题长（信息更完整）

用法：
    python3 scripts/dedupe_news.py --dry-run    # 只报告，不改动
    python3 scripts/dedupe_news.py              # 实际清理
"""

import argparse
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from dedupe_lib import SimilarIndex   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
HTML_PATH = os.path.join(ROOT, "index.html")
BACKUP_DIR = os.path.join(ROOT, "backups")
START_MARK = "/* <<<SEED_DATA_START>>> */"
END_MARK = "/* <<<SEED_DATA_END>>> */"
CST = timezone(timedelta(hours=8))

# 正规媒体，保留时优先
TRUSTED = [
    "reuters", "bloomberg", "ft.com", "wsj", "cnbc", "forbes", "the verge",
    "engadget", "ign", "gamespot", "polygon", "eurogamer", "pcgamer",
    "techcrunch", "scmp", "straitstimes", "nikkei", "yahoo", "investing.com",
    "kotaku", "gamesindustry", "videogameschronicle", "gamedeveloper",
    "vg247", "dexerto", "gamesradar", "bbc", "the guardian", "independent",
    "telegraph", "marketwatch", "seeking alpha", "economic times",
    "channel news asia", "cna", "financial post", "retail dive",
    "thepaper", "澎湃", "凤凰", "新浪", "界面", "36氪", "虎嗅", "经济观察",
    "第一财经", "财新", "联合早报", "ubisoft", "prnewswire",
]

# 明显不是新闻的噪声（多是聚合站的个人频道，如 "electrostreet's Library"）
NOISE_PATTERNS = [
    r"^[\u4e00-\u9fff]{2,6}图书馆$",          # 译后的 "XX's Library"
    r"\b\w+'s\s+Library\b",                    # 未译的原文
]


def is_noise(it):
    t = (it.get("title") or "").strip()
    for p in NOISE_PATTERNS:
        if re.search(p, t, re.I):
            return True
    return False


def keep_score(it):
    """同一去重键下，分数高的保留。"""
    src = (it.get("source") or "").lower()
    s = 0
    if it.get("summary"):
        s += 1000
    for t in TRUSTED:
        if t in src:
            s += 500
            break
    if "bing" in src:
        s += 100
    # 日期新的优先（字符串可直接比较）
    s += int((it.get("date") or "").replace("-", "") or 0) / 1e8
    # 标题信息量
    s += min(len(it.get("title") or ""), 80) / 100
    return s


def read_seed(html):
    s = html.find(START_MARK)
    e = html.find(END_MARK)
    if s < 0 or e < 0:
        sys.exit("[FAIL] index.html 里找不到 SEED_DATA 标记")
    block = html[s + len(START_MARK):e]
    m = re.search(r"const\s+SEED_DATA\s*=\s*(\[.*?\])\s*;", block, re.S)
    if not m:
        sys.exit("[FAIL] SEED_DATA 区块解析失败")
    return json.loads(m.group(1)), s, e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="只报告不改动")
    args = ap.parse_args()

    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()
    seed, s, e = read_seed(html)
    print("  原始条目 %d 条" % len(seed))

    # 1) 清理噪声
    noises = [x for x in seed if is_noise(x)]
    clean = [x for x in seed if not is_noise(x)]
    if noises:
        print("\n  === 噪声条目 %d 条 ===" % len(noises))
        for x in noises[:10]:
            print("    [%s] %s" % (x.get("source", "")[:14], (x.get("title") or "")[:44]))

    # 2) 按标题去重：精确键 + 2-gram 相似度兜底（逻辑见 dedupe_lib.py）

    # 按 keep_score 降序处理，保证同一事件留下的总是质量最高的那条
    # （有摘要 > 来源可信 > 日期新）
    kept, dups = [], []
    sim = SimilarIndex()
    for x in sorted(clean, key=keep_score, reverse=True):
        if sim.find(x.get("title"), x.get("topic")) is not None:
            dups.append(x)
            continue
        sim.add(x)
        kept.append(x)
    if dups:
        print("\n  === 重复条目 %d 条（每组保留 1 条）===" % len(dups))
        for x in dups[:12]:
            print("    [%s] %s" % (x.get("date", ""), (x.get("title") or "")[:46]))
        if len(dups) > 12:
            print("    … 另有 %d 条" % (len(dups) - 12))

    removed = len(noises) + len(dups)
    print("\n  汇总：清理噪声 %d 条 + 重复 %d 条 = 删除 %d 条，剩余 %d 条"
          % (len(noises), len(dups), removed, len(kept)))

    if args.dry_run:
        print("\n  [dry-run] 未改动任何文件")
        return
    if removed == 0:
        print("\n  没有需要清理的内容")
        return

    # 备份
    os.makedirs(BACKUP_DIR, exist_ok=True)
    stamp = datetime.now(CST).strftime("%Y%m%d-%H%M%S")
    shutil.copy2(HTML_PATH, os.path.join(BACKUP_DIR, "index-%s.html" % stamp))

    kept.sort(key=lambda i: (str(i.get("date") or ""), str(i.get("topic") or "")), reverse=True)
    version = datetime.now(CST).strftime("%Y-%m-%dT%H:%M")
    new_block = (START_MARK + "\nconst SEED_DATA = "
                 + json.dumps(kept, ensure_ascii=False, indent=2)
                 + ";\nconst DATA_VERSION = \"" + version + "\";\n" + END_MARK)
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(html[:s] + new_block + html[e + len(END_MARK):])
    print("\n[OK] 已写入 index.html（备份 backups/index-%s.html）" % stamp)


if __name__ == "__main__":
    main()
