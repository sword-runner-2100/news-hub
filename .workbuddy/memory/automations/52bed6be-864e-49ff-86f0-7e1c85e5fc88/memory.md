# 自动化执行记忆：news-hub 当日摘要（育碧 / Temu）

## 抓取方法（已验证，复用即可）
- `curl -sL https://sword-runner-2100.github.io/news-hub/ -o /tmp/news_hub_index.html`
- 页面是单文件、无外部 fetch，新闻数据全在内嵌 `SEED_DATA` 数组里。
- 解析：按标记 `/* <<<SEED_DATA_START>>> */` 与 `/* <<<SEED_DATA_END>>> */` 切段，取首尾 `[` `]` 之间内容 `json.loads`。
- 字段：`id / date（入库日期）/ topic（ubisoft|temu）/ cat / title / summary / source / url / pubDate（原文发布日期）`。
- `DATA_VERSION` 常量即页面数据时间戳（如 `2026-10-11T01:43`）。
- 「今天新增」= `date` 等于北京时间当天的条目，不要按 `pubDate` 过滤（pubDate 常比入库早 1-2 天）。

## 输出约定
- 分组：育碧 / Temu；无新增时明确写「今日无新增」，不得外搜补数。
- LinkedIn 官方帖类条目单独标「官方发布」；没有就写「今日无」。
- 每条一句话概括 + 来源 + 原文链接；末尾 3 条核心看点。
- 严禁编造：只用页面 title/date/url，标题未点名的公司不指认。

## 执行记录
- 2026-10-11 09:21：共 301 条数据；当天新增 3 条全部为 Temu（Nikkei Asia / Retail Dive / Yahoo Finance，pubDate 均为 2026-10-09），育碧 0 条、官方发布 0 条。产出 `reports/2026-10-11-每日摘要.md`。
- 2026-10-12 09:21：今日无新增。数据仍为 301 条（与昨日完全一致），DATA_VERSION 已刷新为 2026-10-12T01:57，但最新入库日期仍为 2026-10-11（Temu）/ 2026-10-10（育碧），说明 01:57 抓取窗口未回数。产出 `reports/2026-10-12-每日摘要.md`。建议后续关注抓取链路是否连续空转。
- 2026-10-13 09:25：新增 6 条（育碧 1 / Temu 5），总量 307，DATA_VERSION=2026-10-13T05:40 —— 10-12 的空转问题已解除，链路恢复正常。LinkedIn 官方帖今日无（最近一批仍为 10-10 三条 Temu MOU 类）。产出 `reports/2026-10-13-每日摘要.md`。
- 2026-10-14 09:26：新增 2 条（育碧 1 / Temu 1），总量 309，DATA_VERSION=2026-10-14T03:48，链路正常但素材量偏少。育碧条为 RPS 关于《刺客信条：黑旗》重制版被删尾声场景遭数据挖掘（传闻级）；Temu 条为 LinkedIn 官方帖（Direct Beauty 订单十倍增长），属「官方发布」。产出 `reports/2026-10-14-每日摘要.md`。注：近期 LinkedIn 官方帖节奏为 10-10 一批 3 条、10-14 一条，间隔不定。
