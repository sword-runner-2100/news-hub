#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 index.html 里已存在的英文条目回译为中文。

用途：翻译功能是后来才加上的，在那之前抓取的条目还是英文原文。
这个脚本扫一遍 SEED_DATA，把非中文的标题/摘要翻译掉，让整页语言统一。

幂等：已经是中文的条目会跳过，重复运行无副作用。

用法：
    python3 scripts/backfill_translate.py              # 翻译并写回 index.html
    python3 scripts/backfill_translate.py --dry-run    # 只统计，不改动
"""

import argparse
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone, timedelta

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import fetch_news as fn  # 复用其中的翻译逻辑

HTML_PATH = os.path.join(ROOT, "index.html")
BACKUP_DIR = os.path.join(ROOT, "backups")
START_MARK = "/* <<<SEED_DATA_START>>> */"
END_MARK = "/* <<<SEED_DATA_END>>> */"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="只统计，不写回")
    args = ap.parse_args()

    html = open(HTML_PATH, encoding="utf-8").read()
    s = html.find(START_MARK)
    e = html.find(END_MARK)
    if s < 0 or e < 0:
        print("[FAIL] 找不到 SEED_DATA 标记")
        sys.exit(1)

    block = html[s + len(START_MARK):e]
    m = re.search(r"const\s+SEED_DATA\s*=\s*(\[.*?\])\s*;", block, re.S)
    if not m:
        print("[FAIL] SEED_DATA 解析失败")
        sys.exit(1)
    items = json.loads(m.group(1))

    pending = [x for x in items if not fn.has_cn(x.get("title", ""))
               or (x.get("summary") and not fn.has_cn(x["summary"]))]
    print("总条目 %d，待翻译 %d" % (len(items), len(pending)))
    if not pending:
        print("[OK] 没有需要翻译的条目")
        return
    if args.dry_run:
        for x in pending[:10]:
            print("  - " + x.get("title", "")[:70])
        return

    cache = {}
    n_t = n_d = 0
    for x in pending:
        t, ok1 = fn.translate_one(x.get("title", ""), cache)
        if ok1:
            n_t += 1
        x["title"] = t
        if x.get("summary"):
            d, ok2 = fn.translate_one(x["summary"], cache)
            if ok2:
                n_d += 1
            x["summary"] = d

    print("[OK] 翻译完成：标题 %d 条、摘要 %d 条" % (n_t, n_d))
    if not (n_t or n_d):
        print("     内容无变化，不写回")
        return

    # 备份后写回（保持原本的缩进风格）
    os.makedirs(BACKUP_DIR, exist_ok=True)
    stamp = datetime.now(timezone(timedelta(hours=8))).strftime("%Y%m%d-%H%M%S")
    shutil.copy2(HTML_PATH, os.path.join(BACKUP_DIR, "index-%s.html" % stamp))

    body = json.dumps(items, ensure_ascii=False, indent=2)
    new_block = START_MARK + "\nconst SEED_DATA = " + body + ";\n"
    # 保留原有的 DATA_VERSION
    vm = re.search(r"const DATA_VERSION = \"([^\"]*)\";", block)
    if vm:
        new_block += "const DATA_VERSION = \"%s\";\n" % vm.group(1)
    new_block += END_MARK

    open(HTML_PATH, "w", encoding="utf-8").write(html[:s] + new_block + html[e + len(END_MARK):])
    print("[OK] 已写回 index.html（备份在 backups/）")


if __name__ == "__main__":
    main()
