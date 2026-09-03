#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日新闻汇总台 —— 数据更新脚本

用法：
    python3 update_news.py --file inbox/2026-08-30.json
    python3 update_news.py --file inbox/2026-08-30.json --keep-days 180

输入 JSON 支持两种格式：
    1) {"date":"2026-08-30","items":[{...},{...}]}
    2) [{...},{...}]                       # 数组形式，date 缺省取今天

单条 item 字段：
    topic    必填  ubisoft | temu
    title    必填  标题
    summary  选填  摘要（1-3 句）
    source   选填  来源媒体名
    url      选填  原文链接（同时作为去重键）
    pubDate  选填  原文发布时间 YYYY-MM-DD
    cat      选填  分类短标签，如 财报 / 监管 / 战略 / 产品
    date     选填  抓取日期 YYYY-MM-DD，缺省取当天

行为：
    - 合并进 index.html 的 SEED_DATA 区块，最新一天置顶
    - 按 url（无 url 则按 title+topic）去重，已存在的不重复写入
    - 自动清理超过 --keep-days 天的历史（默认 180 天，0 表示不清理）
    - 每次改动前自动备份 index.html 到 backups/（保留最近 10 份）
    - 更新 DATA_VERSION 为当前时间戳，页面据此判断是否有新内容
"""

import argparse
import json
import os
import re
import shutil
import sys
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
HTML_PATH = os.path.join(ROOT, "index.html")
BACKUP_DIR = os.path.join(ROOT, "backups")
START_MARK = "/* <<<SEED_DATA_START>>> */"
END_MARK = "/* <<<SEED_DATA_END>>> */"
VALID_TOPICS = ("ubisoft", "temu")
CST = timezone(timedelta(hours=8))


def die(msg):
    print("[FAIL] " + msg, file=sys.stderr)
    sys.exit(1)


def today():
    return datetime.now(CST).strftime("%Y-%m-%d")


def slugify(text, maxlen=60):
    s = re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "-", str(text or "")).strip("-").lower()
    return (s[:maxlen] or "item")


def title_key(t):
    """标题去重键：去标点空格后取前 40 字。

    只按 url 去重是不够的 —— Google 源的链接是加密中转地址，同一篇文章换个关键词
    或市场抓回来 url 就变了；Bing 的中转链接解析失败时也会退化成不同地址。
    结果就是同一事件反复入库（实测同一标题重复 4 次）。
    """
    return re.sub(r"[\s\W_]+", "", str(t or "")).lower()[:40]


def prefix_key(t):
    """标题前 12 字，用作相似度比较的分桶键（避免全表 O(n²) 比较）。"""
    return re.sub(r"[\s\W_]+", "", str(t or "")).lower()[:12]


def _grams(t, n=2):
    s = re.sub(r"[\s\W_]+", "", str(t or "")).lower()
    return {s[i:i + n] for i in range(len(s) - n + 1)} or {s}


def similar(a, b, thresh=0.35):
    """两个标题是否描述同一事件（Jaccard 相似度）。

    兜住「同一事件、不同译法」：翻译接口不是确定性的，同一篇报道隔天抓回来可能译出
    「Ubisoft游戏正式结束对多个平台的支持」和「Ubisoft游戏正式结束多平台支持」，
    精确去重键抓不到，但读者看到的是两条几乎一样的新闻。

    阈值取 0.35，实测样本分布：同一事件的不同译法 0.41~0.62，
    仅共享游戏名的不同新闻 0.14，两侧都有余量。
    """
    ga, gb = _grams(a), _grams(b)
    if not ga or not gb:
        return False
    union = len(ga | gb)
    return bool(union) and len(ga & gb) / union >= thresh


def normalize(item, fallback_date):
    if not isinstance(item, dict):
        return None
    title = str(item.get("title") or "").strip()
    topic = str(item.get("topic") or "").strip().lower()
    if not title:
        return None
    if topic not in VALID_TOPICS:
        return None
    url = str(item.get("url") or "").strip()
    ident = str(item.get("id") or "").strip()
    if not ident:
        key = url if url else (topic + "|" + title)
        ident = topic + "-" + re.sub(r"[^0-9a-zA-Z]", "", (fallback_date or "")) + "-" + slugify(key)
    pub = str(item.get("pubDate") or "").strip()
    if pub:
        m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", pub)
        pub = m.group(0) if m else ""
    return {
        "id": ident,
        "date": str(item.get("date") or fallback_date or today()).strip(),
        "topic": topic,
        "cat": str(item.get("cat") or "").strip()[:12],
        "title": title[:200],
        "summary": str(item.get("summary") or "").strip()[:600],
        "source": str(item.get("source") or "").strip()[:60],
        "url": url,
        "pubDate": pub,
    }


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


def read_seed(html):
    s = html.find(START_MARK)
    e = html.find(END_MARK)
    if s < 0 or e < 0:
        die("index.html 里找不到 SEED_DATA 标记，页面结构可能被改动过")
    block = html[s + len(START_MARK):e]
    m = re.search(r"const\s+SEED_DATA\s*=\s*(\[.*?\])\s*;", block, re.S)
    if not m:
        die("SEED_DATA 区块解析失败")
    try:
        data = json.loads(m.group(1))
    except Exception as ex:
        die("SEED_DATA 不是合法 JSON：%s" % ex)
    return data, s, e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True, help="待导入的新闻 JSON 文件路径")
    ap.add_argument("--keep-days", type=int, default=180, help="保留最近 N 天，0 表示不清理")
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

    if isinstance(payload, dict):
        fetch_date = str(payload.get("date") or today()).strip()
        raw = payload.get("items") or []
    elif isinstance(payload, list):
        fetch_date = today()
        raw = payload
    else:
        die("输入 JSON 必须是对象或数组")

    incoming = [x for x in (normalize(i, fetch_date) for i in raw) if x]
    if not incoming:
        die("没有合法的新闻条目（检查 topic 是否为 ubisoft/temu、title 是否为空）")

    with open(HTML_PATH, "r", encoding="utf-8") as f:
        html = f.read()

    seed, s, e = read_seed(html)

    # 双索引去重：url 挡住完全相同的抓取，标题挡住「同一事件、不同链接」。
    # 保留哪条：已存在的优先（先入库的通常是可信度排序更靠前的那条）。
    index = {}       # url/id → item
    by_title = {}    # 归一化标题 → item
    by_prefix = {}   # 前 12 字 → [item]，供相似度兜底查询
    for it in seed:
        if not isinstance(it, dict):
            continue
        key = (it.get("url") or "").strip() or str(it.get("id") or "")
        if key:
            index[key] = it
        tk = title_key(it.get("title") or "")
        if tk and tk not in by_title:
            by_title[tk] = it
        pk = prefix_key(it.get("title") or "")
        if pk:
            by_prefix.setdefault(pk, []).append(it)

    added, dup_url, dup_title, dup_sim = 0, 0, 0, 0
    for it in incoming:
        key = it["url"] or it["id"]
        tk = title_key(it["title"])
        # 1) 标题完全一致（换了链接的同一条）
        if tk and tk in by_title:
            dup_title += 1
            continue
        # 2) 标题不同但足够相似（同一事件的不同译法 / 不同媒体报道）
        hit = None
        for other in by_prefix.get(prefix_key(it["title"]), []):
            if other.get("topic") == it.get("topic") and \
                    similar(it["title"], other.get("title")):
                hit = other
                break
        if hit is not None:
            dup_sim += 1
            continue
        # 3) 链接完全相同
        if key in index:
            dup_url += 1
            continue
        index[key] = it
        if tk:
            by_title[tk] = it
        pk = prefix_key(it["title"])
        if pk:
            by_prefix.setdefault(pk, []).append(it)
        added += 1

    if dup_title:
        print("     标题去重：拦下 %d 条（同一新闻换了链接被反复抓到）" % dup_title)
    if dup_sim:
        print("     相似去重：拦下 %d 条（同一事件的不同译法 / 不同媒体报道）" % dup_sim)
    if dup_url:
        print("     链接去重：拦下 %d 条" % dup_url)

    merged = list(index.values())

    pruned = 0
    if args.keep_days and args.keep_days > 0:
        cutoff = (datetime.now(CST) - timedelta(days=args.keep_days)).strftime("%Y-%m-%d")
        before = len(merged)
        merged = [i for i in merged if str(i.get("date") or "") >= cutoff]
        pruned = before - len(merged)

    merged.sort(key=lambda i: (str(i.get("date") or ""), str(i.get("topic") or "")), reverse=True)

    version = datetime.now(CST).strftime("%Y-%m-%dT%H:%M")
    body = json.dumps(merged, ensure_ascii=False, indent=2)
    new_block = (
        START_MARK
        + "\nconst SEED_DATA = "
        + body
        + ";\nconst DATA_VERSION = \""
        + version
        + "\";\n"
        + END_MARK
    )

    if not args.no_backup:
        backup()

    new_html = html[:s] + new_block + html[e + len(END_MARK):]
    with open(HTML_PATH, "w", encoding="utf-8") as f:
        f.write(new_html)

    counts = {}
    for i in merged:
        counts[i["topic"]] = counts.get(i["topic"], 0) + 1
    newest = merged[0]["date"] if merged else "-"

    print("[OK] 写入完成")
    print("     新增 %d 条 / 清理 %d 条 / 总计 %d 条" % (added, pruned, len(merged)))
    print("     育碧 %d 条，Temu %d 条" % (counts.get("ubisoft", 0), counts.get("temu", 0)))
    print("     最新日期 %s  数据版本 %s" % (newest, version))
    if added == 0:
        print("     提示：本次未新增，可能是内容与已抓取的重复")


if __name__ == "__main__":
    main()
