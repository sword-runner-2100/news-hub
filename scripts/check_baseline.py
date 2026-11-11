#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日新闻汇总台 —— 不可回退基线检查 + 最小上下文包生成（只读，不修改任何文件）

把「用户已形成的使用习惯」和「上一轮刚修好的可见性缺陷」写成可执行断言，
任何后续重构（尤其是交给 Hy4/其他模型做会话侧改造）跑一遍就能发现回归。

用法：
    python3 scripts/check_baseline.py                 # 全绿则退出码 0
    python3 scripts/check_baseline.py --self-test     # 额外验证「故意改坏能被抓到」
    python3 scripts/check_baseline.py --map           # 输出不含数据的逻辑骨架地图（供模型会话固定上下文）
    python3 scripts/check_baseline.py --json          # 机器可读结果

设计约束：零第三方依赖；不写文件、不联网、不调用任何 LLM；
运行时不引入任何新的外部依赖，本脚本也不挂进 GitHub Actions（避免误报阻断数据刷新）。
"""
import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

MARKS = [
    ("SEED", "/* <<<SEED_DATA_START>>> */", "/* <<<SEED_DATA_END>>> */"),
    ("STEAM", "/* <<<STEAM_DATA_START>>> */", "/* <<<STEAM_DATA_END>>> */"),
    ("YOUTUBE", "/* <<<YOUTUBE_DATA_START>>> */", "/* <<<YOUTUBE_DATA_END>>> */"),
]
FILES = [
    "index.html",
    "scripts/update_news.py",
    "scripts/update_youtube.py",
    "scripts/dedupe_lib.py",
    "scripts/fetch_steam.py",
    ".github/workflows/refresh.yml",
]


def load_all():
    out = {}
    for rel in FILES:
        with open(os.path.join(ROOT, rel), "r", encoding="utf-8") as f:
            out[rel] = f.read()
    return out


def parse_data(html):
    """把三个内联数据块解析成 Python 对象，只用于校验，绝不回写。"""
    blocks = {}
    for name, a, b in MARKS:
        i, j = html.find(a), html.find(b)
        if i < 0 or j <= i:
            raise ValueError("标记块缺失或顺序错乱: " + name)
        blocks[name] = html[i + len(a):j]

    seed = json.loads(
        re.search(r"const\s+SEED_DATA\s*=\s*(\[.*?\])\s*;", blocks["SEED"], re.S).group(1))
    from update_youtube import balanced_object, eval_js_object

    def js_obj(name):
        blk = blocks[name]
        i, j = balanced_object(blk, name + "_DATA")
        return eval_js_object(blk[i:j])

    return {"seed": seed, "steam": js_obj("STEAM"), "youtube": js_obj("YOUTUBE")}


def run_checks(files):
    R = []

    def chk(name, ok, detail=""):
        R.append({"name": name, "ok": bool(ok), "detail": str(detail)})

    html = files["index.html"]
    un = files["scripts/update_news.py"]
    uy = files["scripts/update_youtube.py"]
    dl = files["scripts/dedupe_lib.py"]
    wf = files[".github/workflows/refresh.yml"]

    # ---- A. 单文件结构契约 ----
    pos = [html.find(a) for _, a, _ in MARKS]
    ends = [html.find(b) for _, _, b in MARKS]
    chk("三个标记块完整且顺序正确",
        all(p >= 0 for p in pos + ends) and pos[0] < ends[0] < pos[1] < ends[1] < pos[2] < ends[2])
    chk("DATA_VERSION 在 SEED 块内且格式合法",
        bool(re.search(r'const DATA_VERSION = "\d{4}-\d{2}-\d{2}T\d{2}:\d{2}"', html[pos[0]:ends[0]])))
    chk("单文件零外部依赖（无外链 JS/CSS/字体）",
        "<script src" not in html and 'rel="stylesheet"' not in html and "@import" not in html)
    chk("页面无内联事件处理器", "onerror=" not in html and "onclick=" not in html)

    # ---- B. 数据契约 ----
    try:
        d = parse_data(html)
        chk("内联数据三块均可解析", True)
    except Exception as ex:
        chk("内联数据三块均可解析", False, ex)
        d = None

    if d:
        seed, games, vids = d["seed"], d["steam"]["games"], d["youtube"]["videos"]
        chk("新闻条目 schema 合法",
            all(isinstance(i, dict) and all(k in i for k in ("id", "title", "topic", "date"))
                and i["topic"] in ("ubisoft", "temu") for i in seed), "%d 条" % len(seed))
        dup = len(seed) - len({i["id"] for i in seed})
        chk("历史 id 碰撞已有复合键防护",
            html.count("!map.has(itemKey(i))") >= 2 and "function itemKey(i)" in html,
            "已知历史碰撞 %d 条（旧版截断 URL 所致，已不丢数据）" % dup)
        cn = sum(1 for i in seed if re.search(r"[\u4e00-\u9fff]", i.get("title", "")))
        chk("中文标题占比 >= 95%", cn / max(1, len(seed)) >= 0.95, "%d/%d" % (cn, len(seed)))
        chk("原文链接可点", all(not i.get("url") or i["url"].startswith(("http://", "https://")) for i in seed))
        chk("Steam AppID 2507950 / 2073620",
            sorted(str(g.get("appId")) for g in games) == ["2073620", "2507950"])
        chk("Steam 近 7 天窗口", len(games) == 2 and all(len(g.get("daily", [])) <= 7 for g in games))
        chk("YouTube videoId 唯一", len({v.get("videoId") for v in vids}) == len(vids), "%d 条" % len(vids))
        ai = [v for v in vids if v.get("aiSummary")]
        chk("AI 总结字段受来源优先级保护",
            "summary_rank" in uy and "carry_summary(ov, nv)" in uy
            and all(v.get("summarySource") == "ai" for v in ai),
            "%d 条 aiSummary" % len(ai))

    # ---- C. 不可回退基线（上一轮「内容看不见」的根因修复）----
    p_state, p_items = html.find("let STATE = readJSON(K.state"), html.find("let ITEMS = loadItems()")
    chk("STATE 先于 ITEMS 初始化", 0 <= p_state < p_items, "loadItems 依赖这个隐式顺序")
    chk("loadItems 的 noReseed 例外", "STATE.noReseed !== String(DATA_VERSION)" in html)
    chk("官方帖蓝色徽章 officialBadge",
        "function officialBadge(i){" in html and 'LinkedIn: "LinkedIn 官方"' in html)
    chk("官方帖免标题去重",
        'official = (it.get("cat") == "官方")' in un and "if not official and sim.find" in un)
    for k in ("wb_newshub_items_v1", "wb_newshub_state_v1", "wb_newshub_view_v1"):
        chk("localStorage key 未改: " + k, k in html)
    chk("STATE 五字段齐备",
        all(x in html for x in ("STATE.read", "STATE.star", "STATE.ytRead", "STATE.ytFold", "noReseed")))

    # ---- D. 业务口径与使用习惯 ----
    m = re.search(r"const TOPICS = \{(.*?)\};", html, re.S)
    keys = re.findall(r"^\s*(\w+):\s*\{name:", m.group(1), re.M) if m else []
    chk("话题枚举恰好 ubisoft / temu", sorted(keys) == ["temu", "ubisoft"], keys)
    chk("话题配色类齐全", all(x in html for x in (".t-ubisoft", ".t-temu", ".b-ubisoft", ".b-temu")))
    chk("去重阈值 SIM_THRESH = 0.45", "SIM_THRESH = 0.45" in dl)
    chk("定时 09:00 / 21:00（UTC 1,13）", "cron: '0 1,13 * * *'" in wf)
    steps = re.findall(r"^\s*- name: (.+)$", wf, re.M)
    chk("workflow 10 个步骤", len(steps) == 10, "%d 步" % len(steps))
    chk("四路抓取 + 微信推送齐备",
        all(x in wf for x in ("fetch_news.py", "fetch_linkedin.py", "fetch_steam.py",
                              "fetch_youtube.py", "push_wechat.py")))
    chk("视图三档 auto / desktop / mobile",
        all(("'" + v + "'") in html or ('"' + v + '"') in html for v in ("auto", "desktop", "mobile")))
    chk("导入导出与清空二次确认",
        all(x in html for x in ("export-json", "export-csv", 'case "import"', "confirm(")))
    chk("新闻按日期最新置顶", "return a.date < b.date ? 1 : -1" in html)
    chk("不恢复「今天要处理」模块", "今天要处理" not in html)

    # ---- E. 本轮优化形成的新基线 ----
    chk("update_news 空变化幂等", "没有检测到变化，页面未改动" in un)
    chk("update_youtube 空变化幂等", "没有检测到变化，页面未改动" in uy)
    chk("added.json 同日累加不覆盖", "carried + added_items" in un)
    chk("新 id 规则带完整 URL 哈希", "hashlib.sha1(key.encode" in un)
    chk("窄屏 .yt-body min-width:0", "flex:1;min-width:0}" in html)
    chk("筛选与搜索偏好持久化", "wb_newshub_prefs_v1" in html and "savePrefs()" in html)
    chk("手机断点单一来源", "window.WB_MOBILE_BP" in html)
    return R


SELF_TESTS = [
    ("破坏 SEED 标记块", lambda h: h.replace("/* <<<SEED_DATA_END>>> */", "/* BROKEN */", 1), "标记块"),
    ("删掉 noReseed 例外", lambda h: h.replace("STATE.noReseed !== String(DATA_VERSION)", "false", 1), "noReseed"),
    ("删掉官方徽章",
     lambda h: h.replace("function officialBadge(i){", "function removedBadge(i){", 1), "officialBadge"),
    ("移除复合键防护",
     lambda h: h.replace("!map.has(itemKey(i))", "!map.has(i.id)"), "复合键"),
    ("调换 STATE / ITEMS 初始化顺序",
     lambda h: h.replace("let STATE = readJSON(K.state, {read:{}, star:{}});\nlet ITEMS = loadItems();",
                         "let ITEMS = loadItems();\nlet STATE = readJSON(K.state, {read:{}, star:{}});", 1),
     "STATE 先于"),
]


def self_test(files):
    base = run_checks(files)
    base_fails = {r["name"] for r in base if not r["ok"]}
    results = []
    for label, mutate, keyword in SELF_TESTS:
        bad = dict(files)
        bad["index.html"] = mutate(files["index.html"])
        changed = bad["index.html"] != files["index.html"]
        after = run_checks(bad)
        new_fails = [r["name"] for r in after if not r["ok"] and r["name"] not in base_fails]
        hit = [n for n in new_fails if keyword in n]
        results.append({"case": label, "ok": bool(changed and hit),
                        "detail": ("抓到: " + ", ".join(hit)) if hit else "未抓到预期回归"})
    return results


def context_map(files):
    """P0-1：给模型会话用的最小上下文包 —— 只输出骨架，绝不输出 86% 的内联数据。"""
    html = files["index.html"]
    lines = html.splitlines()
    out = ["# news-hub 最小上下文包（自动生成，不含任何内联数据）", "",
           "> 用途：后续让模型改代码时把本文件当固定上下文，避免把 86% 的数据块塞进会话。", ""]
    out.append("## 规模")
    out.append("- index.html：%d 行 / %d 字节，单文件、CSS/JS 全内联、零外部依赖" %
               (len(lines), len(html.encode("utf-8"))))
    out.append("")
    out.append("## 只读数据区（严禁误写）")
    out.append("| 标记块 | 起始行 | 结束行 | 字节 |")
    out.append("|---|---:|---:|---:|")
    for name, a, b in MARKS:
        s = next((i + 1 for i, l in enumerate(lines) if a in l), -1)
        e = next((i + 1 for i, l in enumerate(lines) if b in l), -1)
        i, j = html.find(a), html.find(b)
        out.append("| %s | %d | %d | %d |" % (name, s, e, j - i))
    try:
        d = parse_data(html)
        out.append("")
        out.append("- SEED_DATA：%d 条新闻（育碧 %d / Temu %d）" %
                   (len(d["seed"]), sum(1 for i in d["seed"] if i["topic"] == "ubisoft"),
                    sum(1 for i in d["seed"] if i["topic"] == "temu")))
        out.append("- STEAM_DATA：%d 款游戏 × 7 天" % len(d["steam"]["games"]))
        out.append("- YOUTUBE_DATA：%d 条视频，其中 %d 条 aiSummary（由仓库外自动化写入）" %
                   (len(d["youtube"]["videos"]),
                    sum(1 for v in d["youtube"]["videos"] if v.get("aiSummary"))))
    except Exception:
        pass
    out.append("")
    out.append("## 逻辑段函数索引（可改写区，行号随数据增长会漂移，以函数名为准）")
    out.append("")
    start = next((i for i, l in enumerate(lines) if "const TOPICS = {" in l), 0)
    for i in range(start, len(lines)):
        m = re.match(r"^function\s+(\w+)\s*\(", lines[i])
        if m:
            out.append("- L%d `%s()`" % (i + 1, m.group(1)))
    out.append("")
    out.append("## localStorage 契约（不可改名 / 不可丢字段）")
    out.append("")
    out.append("| key | 内容 |")
    out.append("|---|---|")
    out.append("| `wb_newshub_items_v1` | `{version, items[]}`，items 为新闻数组 |")
    out.append("| `wb_newshub_state_v1` | `{read, star, ytRead, ytFold, noReseed}`，旧快照必须可打开 |")
    out.append("| `wb_newshub_view_v1` | `auto / desktop / mobile` 三档 |")
    out.append("| `wb_newshub_prefs_v1` | `{filter, query}`，刷新后恢复筛选与搜索词 |")
    out.append("")
    out.append("## 运行时编排（GitHub Actions，不是模型）")
    out.append("")
    steps = re.findall(r"^\s*- name: (.+)$", files[".github/workflows/refresh.yml"], re.M)
    for i, s in enumerate(steps, 1):
        out.append("%d. %s" % (i, s))
    out.append("")
    out.append("## 红线（模型不得提议改动）")
    out.append("")
    for x in ["固定网址与 GitHub Pages 部署、单文件零 CDN、离线可开",
              "每天 09:00 / 21:00 云端自动更新，不依赖电脑开机",
              "三个标记块与 DATA_VERSION 语义、update 脚本幂等",
              "话题枚举 ubisoft/temu、AppID 2507950/2073620、Steam 7 天窗口",
              "已读/星标/筛选/搜索/视图三档/导入导出/清空二次确认",
              "新闻按日期最新置顶、中文标题、原文链接可点",
              "官方帖徽章 + 官方帖免去重 + loadItems 补新 / noReseed + 复合键防 id 碰撞",
              "摘要只取真实来源、禁止 AI 编造；原文链接必须可点",
              "运行时不引入付费 LLM / 新密钥 / 新常驻外部依赖（Hy4 只在会话侧与离线环节）"]:
        out.append("- " + x)
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true", help="验证故意改坏能被抓到")
    ap.add_argument("--map", action="store_true", help="输出不含数据的最小上下文包")
    ap.add_argument("--json", action="store_true", help="机器可读结果")
    args = ap.parse_args()

    files = load_all()
    if args.map:
        print(context_map(files))
        return 0

    results = run_checks(files)
    failed = [r for r in results if not r["ok"]]
    st = self_test(files) if args.self_test else None

    if args.json:
        print(json.dumps({"checks": results, "self_test": st,
                          "passed": len(results) - len(failed), "failed": len(failed)},
                         ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(("  [OK]   " if r["ok"] else "  [FAIL] ") + r["name"] +
                  (("  — " + r["detail"]) if r["detail"] else ""))
        print("\n基线检查：%d 项通过 / %d 项失败（共 %d 项）" %
              (len(results) - len(failed), len(failed), len(results)))
        if st is not None:
            print("\n自检（故意改坏 → 能否抓到）：")
            for c in st:
                print(("  [OK]   " if c["ok"] else "  [FAIL] ") + c["case"] + " — " + c["detail"])
            bad_st = [c for c in st if not c["ok"]]
            if bad_st:
                failed.extend([{"name": "自检:" + c["case"]} for c in bad_st])

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
