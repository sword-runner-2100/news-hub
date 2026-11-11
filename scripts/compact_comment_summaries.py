#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 index.html 里存量的 YouTube「评论区总结」压成一行结论（一次性迁移，可重复运行/幂等）。

背景：旧的 commentSummary 用文字复述了情绪百分比和主题次数，而卡片上已经有
情绪条、主题标签和热评原文，属于三重重复；其中还有大量「整体中性：0% 正面、0% 负面」
这类没有信息量的套话。生成规则已在 fetch_youtube.py 同步改掉，本脚本负责清洗存量。

规则全部来自已有的真实统计字段，不引入任何推测或 AI 生成内容：
    - 原文明示「评论区不可用」→ 评论区不可用
    - 原文明示「评论较少 / 样本不足」→ 评论样本少
    - 其余按 sentiment.pos / sentiment.neg 用与生成脚本相同的阈值判倾向
    - 中性且无倾向 → 空串（页面不渲染该块）

只替换 YOUTUBE_DATA 块里的 commentSummary 值，其余字节（含其他两个数据标记块）
完全不动。改动前自动备份到 backups/。
"""
import json
import os
import re
import shutil
import sys
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

HTML_PATH = os.path.join(ROOT, "index.html")
BACKUP_DIR = os.path.join(ROOT, "backups")
START_MARK = "/* <<<YOUTUBE_DATA_START>>> */"
END_MARK = "/* <<<YOUTUBE_DATA_END>>> */"
CST = timezone(timedelta(hours=8))

from update_youtube import balanced_object, eval_js_object  # noqa: E402

PAT = re.compile(r'("commentSummary"\s*:\s*)"((?:[^"\\]|\\.)*)"')


def compact(v):
    """按已有真实字段得出一句极短结论；无任何倾向时返回空串。"""
    old = str(v.get("commentSummary") or "")
    if "不可用" in old:
        return "评论区不可用"
    if "评论较少" in old or "不足以" in old or old == "评论样本少":
        return "评论样本少"
    s = v.get("sentiment") or {}
    pos, neg = int(s.get("pos") or 0), int(s.get("neg") or 0)
    if pos >= neg + 20:
        return "偏正面"
    if neg >= pos + 20:
        return "偏负面"
    if pos < 15 and neg < 15:
        return ""
    return "正负掺半"


def backup():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    stamp = datetime.now(CST).strftime("%Y%m%d-%H%M%S")
    dst = os.path.join(BACKUP_DIR, "index-%s.html" % stamp)
    shutil.copy2(HTML_PATH, dst)
    olds = sorted(f for f in os.listdir(BACKUP_DIR)
                  if f.startswith("index-") and f.endswith(".html"))
    for f in olds[:-10]:
        try:
            os.remove(os.path.join(BACKUP_DIR, f))
        except OSError:
            pass
    return dst


def main():
    html = open(HTML_PATH, encoding="utf-8").read()
    s, e = html.find(START_MARK), html.find(END_MARK)
    if s < 0 or e <= s:
        print("[FAIL] 找不到 YOUTUBE_DATA 标记块", file=sys.stderr)
        return 1
    block = html[s + len(START_MARK):e]
    i, j = balanced_object(block, "YOUTUBE_DATA")
    data = eval_js_object(block[i:j])
    videos = data.get("videos") or []

    matches = list(PAT.finditer(block))
    if len(matches) != len(videos):
        print("[FAIL] commentSummary 出现 %d 次，视频 %d 条，无法安全对应"
              % (len(matches), len(videos)), file=sys.stderr)
        return 1

    changed = 0
    counts = {}
    # 从后往前替换，前面的匹配位置不受影响
    for idx in range(len(matches) - 1, -1, -1):
        m = matches[idx]
        new_val = compact(videos[idx])
        counts[new_val or "(不渲染)"] = counts.get(new_val or "(不渲染)", 0) + 1
        replacement = m.group(1) + json.dumps(new_val, ensure_ascii=False)
        if block[m.start():m.end()] == replacement:
            continue
        block = block[:m.start()] + replacement + block[m.end():]
        changed += 1

    if not changed:
        print("[OK] 已是精简版，页面未改动")
        return 0

    backup()
    new_html = html[:s + len(START_MARK)] + block + html[e:]
    open(HTML_PATH, "w", encoding="utf-8").write(new_html)
    print("[OK] 精简 %d 条评论区总结；分布：%s"
          % (changed, "、".join("%s %d 条" % (k, v) for k, v in
                               sorted(counts.items(), key=lambda kv: -kv[1]))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
