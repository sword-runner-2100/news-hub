# 每日新闻汇总台（云端版）

一个固定网址的网页工作台，追踪**育碧 / 拼多多 Temu** 每日新闻与两款游戏的 Steam 在线人数。
全部更新由 GitHub Actions 在云端完成，**不依赖任何人的电脑开机**。

## 它怎么工作

```
GitHub Actions 定时触发（每天 UTC 01:00 / 13:00，即北京 09:00 / 21:00）
   ├─ scripts/fetch_news.py   抓新闻  → 更新 index.html
   ├─ scripts/fetch_steam.py  抓 Steam → 更新 index.html
   └─ git commit + push
              ↓
   GitHub Pages 自动发布（约 1 分钟内生效）
```

页面是**单文件 HTML**，数据直接内联在里面，所以离线也能打开、不依赖任何 CDN。

## 数据源

### 新闻：双源互补

| 源 | 作用 | 说明 |
|---|---|---|
| Google News RSS | 保数量与时效 | 支持 `when:3d` 语法精准过滤最近 3 天，单话题 20–60 条，提供准确来源名 |
| Bing News RSS | 保质量 | `description` 是正文前几句的**真实摘要**，且链接是标准 302 中转，可解析出原文直链 |

- **不用 Google News 的链接做直链**：它是加密的 protobuf 中转地址（`news.google.com/rss/articles/CBMi...`），只能逆向 Google 内部接口解码，太脆弱。浏览器点击仍能跳转原文。
- **Bing 只抓英文**：实测 `setmkt=zh-CN` 时 Bing 返回 HTML 而非 RSS。
- **摘要不靠 AI 编造**：全部来自 Bing 的正文片段，不做任何推测或补充。
- **全网英文源**：Google 13 路 + Bing 14 路，共 27 路并发抓取。抓到的英文条目全部自动译成中文，页面中文标题占比 98%。
- **不抓中文源**：Google News 的中文源博彩 SEO 站占比过高（实测 24 条里 15 条是垃圾），清洗成本远高于收益。
- **翻译走免费接口**：Google 公开翻译端点为主、MyMemory 为备，无需任何 API key。想保留英文原文加 `--no-translate`。
- **垃圾过滤**（必须做）：博彩/SEO 站会把广告词混进 Google News 中文源，实测「育碧」24 条里能有 15 条是这类垃圾。脚本内置关键词黑名单、来源黑名单、标题竖线数判定，以及 `'s Library` 这类个人频道噪声，自动丢弃。

### 翻译质量的三道保险

机器翻译直接套用会出不少洋相，所以加了几层处理：

1. **品牌名占位符保护** —— 翻译前把 Temu / PDD Holdings / Ubisoft / Rainbow Six 等 38 个专有名词换成占位符，译后还原。不这么做 Temu 会被音译成「特姆」「特木」。
   - 占位符必须带词边界 `(?<!\w)...(?!\w)`：否则 `Anno`（纪元这款游戏）会把 `announces` 切成 `QXnQXunces`，整句结构被打断，翻译接口就会乱翻。
2. **术语预替换** —— Trailer→预告片、Season Pass→赛季通行证、price target→目标价、year-on-year→同比 等 16 条。同样走占位符，否则译好的中文术语会被翻译接口二次处理（「免费游玩」曾被改成「免费站立」）。
3. **中英混合标题豁免** —— 含 3 个以上中文字符就不送翻译，避免把「Ubisoft正式确认Rainbow Six自己的XCOM」这类标题翻坏。

**历史条目回填**：翻译功能是后来加的，之前抓的还是英文。
`scripts/backfill_translate.py` 可把存量英文条目批量回译（幂等，可重复运行）。

### 去重：为什么不能只靠 url

早期只按 url 去重，而 Google 源的链接是**加密中转地址**（`news.google.com/rss/articles/CBMi...`），
同一篇文章换个关键词或市场抓回来 url 就变了。结果同一事件反复入库 ——
实测全站 168 条里有 48 条是重复，「Ubisoft 出售了一款游戏…」一条出现 4 次。

三道去重（逻辑集中在 `scripts/dedupe_lib.py`，增量和存量共用）：

1. **精确键** —— 标题去标点后取前 40 字比对
2. **2-gram 相似度** —— 兜住「同一事件、不同译法」。翻译接口不是确定性的，
   同一篇报道会译出「结束对多个平台的支持」和「结束多平台支持」这种字面不同但同源的标题
3. **url** —— 兜底

相似度用 **overlap 系数**（交集 / 较小集合）而非 Jaccard：同一事件的两条报道常常一长一短，
Jaccard 惩罚长度差（0.275），overlap 才如实反映「短的被长的包含」（0.483）。

两个反直觉的坑：

- **剔除 25 字符以上的英文专名**。`Assassin's Creed Black Flag Resynced` 归一化后有 31 个字符，
  单它一个就贡献几十个 gram，会把「更新 1.0.7 发布」和「传言将登陆 Switch 2」这两条**不同新闻**
  顶到 0.66 判定为重复。但短专名（Temu、Ubisoft、Poşta Română）必须保留 ——
  剔掉后「Temu 与罗马尼亚邮政签署协议」和「Poşta Română 与 Temu 达成合作」就对不上了。
- **阈值宁松勿紧**。0.45 是实测卡出来的（同一事件 0.46~0.82，不同新闻 0.00~0.29）。
  漏合并只是多显示一条重复，误杀是真的丢新闻，后者找不回来。

`scripts/dedupe_news.py` 用于清洗存量（幂等，可重复运行），本次把 131 条洗到 94 条。

### Steam 在线人数

SteamCharts 的非公开数据端点：

```
https://steamcharts.com/app/<appId>/chart-data.json
→ [[毫秒时间戳, 在线人数], ...]
```

前段是月度点，后段细化到**每小时采样**。按 UTC 日期分桶，取 max 作日峰值、mean 作日均值。

| 游戏 | AppID |
|---|---|
| Delta Force（三角洲行动） | 2507950 |
| Arena Breakout: Infinite（暗区突围：无限） | 2073620 |

## 目录结构

```
index.html                      页面本体（数据内联在 SEED_DATA / STEAM_DATA 标记块里）
scripts/
  fetch_news.py                 抓新闻（Google + Bing 双源，自动译中）
  fetch_steam.py                抓 Steam 日度数据
  update_news.py                把新闻合并进 index.html（去重、排序、备份）
  update_steam.py               把 Steam 数据合并进 index.html
  backfill_translate.py         把存量英文条目批量回译（幂等）
  dedupe_lib.py                 去重工具（精确键 + 2-gram 相似度），增量与存量共用
  dedupe_news.py                清洗存量重复条目（幂等）
.github/workflows/refresh.yml   定时任务
```

数据在 HTML 里用标记块包裹，脚本按标记整段替换并递增 `DATA_VERSION`：

```js
/* <<<SEED_DATA_START>>> */
const SEED_DATA = [...];
const DATA_VERSION = "...";
/* <<<SEED_DATA_END>>> */
```

## 本地跑一次

```bash
python3 scripts/fetch_news.py --no-update    # 只抓不写，看看抓到了什么
python3 scripts/fetch_news.py                # 抓 + 写入 index.html
python3 scripts/fetch_steam.py               # 刷新 Steam 数据
```

常用参数：

| 脚本 | 参数 | 说明 |
|---|---|---|
| fetch_news.py | `--days 3` | Google 源保留最近 N 天 |
| fetch_news.py | `--bing-days 7` | Bing 源时间窗（它带摘要但更新慢，窗口放宽） |
| fetch_news.py | `--max 8` | 每个话题最多保留 N 条 |
| fetch_news.py | `--no-translate` | 跳过中文翻译 |
| fetch_steam.py | `--days 7` | 保留最近 N 天 |

脚本都是幂等的：数据没变化就不改动文件，并给出提示。

## 部署步骤

已部署完成，当前线上：

- **网址**：https://sword-runner-2100.github.io/news-hub/
- **仓库**：https://github.com/sword-runner-2100/news-hub
- **Pages 来源**：main 分支根目录

若要在别处重新部署：

1. 在 GitHub 上新建一个**空仓库**（不要勾选 README / .gitignore）
2. 在本目录执行 `bash setup.sh`，会自动完成登录、建仓、推送、开启 Pages
3. 或手动：
   ```bash
   git remote add origin https://github.com/<用户名>/<仓库名>.git
   git branch -M main
   git push -u origin main
   ```
   然后到 **Settings → Pages**，Source 选 `Deploy from a branch`，Branch 选 `main`、目录选 `/ (root)`

想立刻验证，到 **Actions** 标签页手动点一次 `刷新新闻汇总台`（`workflow_dispatch` 已开启）。

## 已知限制

- **翻译非 AI**：走免费机器翻译接口，偶尔会有生硬或轻微误译（尤其是双关语）。原文链接始终保留，可点开核对。
- **链接**：Google 源的条目是 `news.google.com` 中转地址，浏览器点击会自动跳转到原文，但不是原文直链。Bing 源的条目已解析成真实直链。
- **摘要覆盖率**：只有 Bing 源给摘要，所以约一半条目有摘要，其余只有标题。
- **Actions 推送冲突**：如果本地也改了 `index.html`，推送前记得先 `git pull --rebase`，因为 Actions 会往同一个分支提交。
