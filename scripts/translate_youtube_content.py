#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
把 index.html 里 YouTube 板块的存量外文内容补译成中文（可重复运行 / 幂等 / 断点续跑）。

为什么需要这个脚本：
    fetch_youtube.py 的 [4/5] 步骤本来就会把标题、内容总结、字幕摘句、章节名、
    热评原文自动检测语种译成中文。但本地 Mac 跑抓取时常用 --no-translate 跳过翻译
    （几十条请求容易超时），这些未译数据直接进了 index.html，于是页面上残留大量外文。

范围（与 fetch_youtube.py 翻译步骤完全一致，等于把存量补到云端正常跑完的状态）：
    title / summary / summaryPoints[].s / chapters[].name / topComments[].text
    aiSummary、commentSummary 本来就是中文；titleOriginal 保留原文，绝不动。

红线：只做语言转换，复用 fetch_youtube.translate_any（sl=auto + 品牌名占位符保护），
不生成原文没有的内容、不改写、不扩写、不做推测；翻译失败一律保留原文。
原文可通过卡片上的原视频链接核对，标题原文另有 titleOriginal 字段留存。

用法：
    python3 scripts/translate_youtube_content.py --dry-run     # 只统计待译量
    python3 scripts/translate_youtube_content.py               # 翻译并写回 index.html
    python3 scripts/translate_youtube_content.py --workers 6   # 调整并发（默认 6）

译文缓存写在 inbox/yt-translation-cache.json（已被 gitignore），命中即跳过，
所以重复运行不会再打接口，中断后重跑也能接着用。
"""
import argparse
import json
import os
import re
import shutil
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

HTML_PATH = os.path.join(ROOT, "index.html")
BACKUP_DIR = os.path.join(ROOT, "backups")
CACHE_PATH = os.path.join(ROOT, "inbox", "yt-translation-cache.json")
START_MARK = "/* <<<YOUTUBE_DATA_START>>> */"
END_MARK = "/* <<<YOUTUBE_DATA_END>>> */"
CST = timezone(timedelta(hours=8))

from update_youtube import balanced_object, eval_js_object, backup  # noqa: E402
from fetch_youtube import translate_any, needs_translation          # noqa: E402

# 只替换这几个字段的值。键名精确匹配，titleOriginal / aiSummary / themes[].name
# 不会被命中（后两者即使命中，值也不在待译映射里）。
VALUE_PAT = re.compile(r'("(?:title|summary|s|name|text)"\s*:\s*)"((?:[^"\\]|\\.)*)"')
TRANSLATABLE_KEYS = ("title", "summary", "s", "name", "text")

# 人工判定的豁免项：中文里夹着型号 / 品牌 / 价格，未译部分全是专有名词，
# 不是「外文内容」。翻译接口对这类碎片会吐回原文或失败，送翻没有意义，
# 明确豁免以免每次重跑都重复打接口。保留原文，不改写、不推测。
NO_TRANSLATE_TEXTS = {
    "RTX 5090 A $12.000 含 Amazon",
}

# 翻译接口明确无法处理的碎片：罗马化马拉雅拉姆语混一个泰米尔语词，
# 实测 sl=auto / ml / ta / en 全部吐回原文。按「失败保留原文、不编造」如实留白。
UNTRANSLATABLE_TEXTS = {
    "Indiayil ninn engnai maniyu cheyyum？",
    "Indiayil ninn engnai மானியு cheyyum？",   # 原始抓取值
}

SKIP_TEXTS = NO_TRANSLATE_TEXTS | UNTRANSLATABLE_TEXTS

# 翻译接口对超长热评只译了后半段，前半段英文整句被原样留下（实测 1 条），
# 另有清单小标题未译。这里只登记人工核对过的普通英文片段及接口真实译文，
# 按首处替换；同一条里的中文、产品型号、人名、方言俚语一律不动
# （翻了反而失真，且不属于内容摘要）。译文来自 fetch_youtube.translate_any，非人工编写。
MANUAL_PATCHES = {
    "Featherboard…had the same issue with the miter bars but really easy fix with "
    "a 3d print miter bar.  After adding the 3d miter bar the featherboard works great.":
        "羽毛板……斜接杆也有同样的问题，但使用 3D 打印斜接杆可以轻松修复。"
        "  添加 3d 斜接杆后，羽毛板效果很好。",
    "Other Items:": "其他物品：",
}

_FOREIGN = r"[A-Za-z\u0400-\u04ff\u3040-\u30ff\u0600-\u06ff\u10a0-\u10ff]{2,}"


def is_translatable(text):
    """是否真的需要送翻（collect_texts 与残留统计共用的同一把尺子）。

    fetch_youtube.needs_translation 只看「汉字数 vs 拉丁字母数」，中文里夹品牌名、
    人名、hashtag 时会被误判成外文，送翻接口只会吐回原文，白耗请求还让脚本不幂等。
    这里补一层：含 ≥2 个汉字且无假名/谚文，就视为已是中文（或已是译文）。
    """
    t = str(text or "").strip()
    if not t or t in SKIP_TEXTS:
        return False
    if not needs_translation(t):
        return False
    if not re.search(_FOREIGN, t):          # 纯符号 / emoji / 数字
        return False
    if len(re.findall(r"[\u4e00-\u9fff]", t)) >= 2 and \
            not re.search(r"[\u3040-\u30ff\uac00-\ud7af]", t):
        return False
    stripped = re.sub(r"#\S+|@\S+|https?://\S+", " ", t)
    return bool(re.search(_FOREIGN, stripped))


def collect_texts(videos):
    """按字段收集需要翻译的原文，返回去重后的列表。"""
    texts = []
    for v in videos:
        for k in ("title", "summary"):
            texts.append(str(v.get(k) or ""))
        for p in v.get("summaryPoints") or []:
            texts.append(str(p.get("s") or ""))
        for ch in v.get("chapters") or []:
            texts.append(str(ch.get("name") or ""))
        for c in v.get("topComments") or []:
            texts.append(str(c.get("text") or ""))
    seen, out = set(), []
    for t in texts:
        if t in seen:
            continue
        seen.add(t)
        if is_translatable(t):
            out.append(t)
    return out


def load_cache():
    try:
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def save_cache(cache):
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    tmp = CACHE_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=1)
    os.replace(tmp, CACHE_PATH)


def translate_batch(texts, cache, workers):
    """并发翻译；失败项最后串行重试一次。返回成功/失败条数。"""
    lock = threading.Lock()
    failed = []
    done = 0

    def work(t):
        local = {}                      # 每线程独立小缓存，避免共享 dict 竞争
        out, ok = translate_any(t, local)
        return t, out, ok

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futs = {pool.submit(work, t): t for t in texts}
        for fu in as_completed(futs):
            t, out, ok = fu.result()
            with lock:
                if ok and out and out != t:
                    cache[t] = out
                    done += 1
                else:
                    failed.append(t)
            if done % 50 == 0 and done:
                print("      …已译 %d / %d" % (done, len(texts)), flush=True)

    # 串行重试，给被限流的请求留一点间隔
    if failed:
        print("      串行重试 %d 条…" % len(failed), flush=True)
        still = []
        for t in failed:
            time.sleep(0.4)
            out, ok = translate_any(t, {})
            if ok and out and out != t:
                cache[t] = out
                done += 1
            else:
                still.append(t)
        failed = still
    return done, failed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="只统计，不请求接口、不改动文件")
    ap.add_argument("--workers", type=int, default=6, help="并发数（默认 6）")
    ap.add_argument("--limit", type=int, default=0, help="只处理前 N 条，用于试跑")
    args = ap.parse_args()

    html = open(HTML_PATH, encoding="utf-8").read()
    s, e = html.find(START_MARK), html.find(END_MARK)
    if s < 0 or e <= s:
        print("[FAIL] 找不到 YOUTUBE_DATA 标记块", file=sys.stderr)
        return 1
    block = html[s + len(START_MARK):e]
    i, j = balanced_object(block, "YOUTUBE_DATA")
    data = eval_js_object(block[i:j])
    videos = data.get("videos") or []

    cache = load_cache()
    done_values = set(cache.values())       # 已经是译文的文本，避免二次送翻
    todo = [t for t in collect_texts(videos) if t not in done_values]
    todo = [t for t in todo if t not in cache]   # 缓存里已有原文→译文，直接用
    if args.limit:
        todo = todo[:args.limit]

    print("[INFO] 视频 %d 条，待译唯一片段 %d 个，缓存命中 %d 个" %
          (len(videos), len(todo), len(cache)), flush=True)
    if args.dry_run:
        print("[OK] dry-run，未请求接口、未改动文件")
        return 0
    if not todo:
        # 缓存里已有译文但页面还没替换过的情况，仍要走写回流程
        print("[INFO] 没有新的待译文本，直接用缓存回填")
    else:
        t0 = time.time()
        ok_n, failed = translate_batch(todo, cache, args.workers)
        save_cache(cache)
        print("[INFO] 翻译成功 %d 条，失败保留原文 %d 条，耗时 %.1fs" %
              (ok_n, len(failed), time.time() - t0), flush=True)

    # 只替换这些字段的字符串值，其余字节（含 titleOriginal、其他两个标记块）完全不动
    matches = list(VALUE_PAT.finditer(block))
    changed = 0
    unchanged_foreign = set()
    for m in reversed(matches):
        try:
            old = json.loads('"' + m.group(2) + '"')
        except ValueError:
            continue
        new = cache[old] if (old in cache and cache[old] != old) else old
        # 精确补译：只把核对过的英文片段换成真实译文，幂等（第二次跑不再命中）
        for frag, rep in MANUAL_PATCHES.items():
            if frag in new:
                new = new.replace(frag, rep, 1)
        if new != old:
            new_literal = json.dumps(new, ensure_ascii=False)
            block = block[:m.start()] + m.group(1) + new_literal + block[m.end():]
            changed += 1
        if is_translatable(old):
            unchanged_foreign.add(old[:60])

    if not changed:
        print("[OK] 页面已是中文，未改动")
        return 0

    backup()
    new_html = html[:s + len(START_MARK)] + block + html[e:]
    open(HTML_PATH, "w", encoding="utf-8").write(new_html)
    print("[OK] 写回 %d 处译文；仍保留原文的外文片段 %d 个（翻译失败，如实留白）"
          % (changed, len(unchanged_foreign)), flush=True)
    if unchanged_foreign:
        for x in list(unchanged_foreign)[:5]:
            print("      - " + x)
    return 0


if __name__ == "__main__":
    sys.exit(main())
