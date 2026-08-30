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
- **中文优先**：排序时中文标题 +200 分、有摘要 +100 分、正规媒体 +50 分。实测每个话题 8 条里通常 7 条以上是中文标题，其余是带真实英文摘要的条目。
- **没有 AI 翻译**：原本打算用 GitHub Models 把英文摘要译成中文，但它已按计划退役，服务端直接返回 `410 github_models_retirement_brownout`。`--translate` 参数保留着，将来有替代推理服务时可直接启用。
- **垃圾过滤**（必须做）：博彩/SEO 站会把广告词混进 Google News 中文源，实测「育碧」24 条里能有 15 条是这类垃圾。脚本内置关键词黑名单、来源黑名单，以及标题竖线数判定，自动丢弃。

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
  fetch_news.py                 抓新闻（Google + Bing 双源，可选翻译）
  fetch_steam.py                抓 Steam 日度数据
  update_news.py                把新闻合并进 index.html（去重、排序、备份）
  update_steam.py               把 Steam 数据合并进 index.html
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

- **新闻链接**：Google 源的条目是 `news.google.com` 中转地址，浏览器点击会自动跳转到原文，但不是原文直链。Bing 源的条目已解析成真实直链。
- **无 AI 翻译**：GitHub Models 退役后，英文条目保留英文原文。中文标题由 Google 中文源直接提供。
- **摘要覆盖率**：只有 Bing 源给摘要，所以约一半条目有摘要，其余只有标题。
- **Actions 推送冲突**：如果本地也改了 `index.html`，推送前记得先 `git pull --rebase`，因为 Actions 会往同一个分支提交。
