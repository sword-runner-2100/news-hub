# 每日新闻汇总台（云端版）

一个固定网址的网页工作台，追踪**育碧 / 拼多多 Temu** 每日新闻与两款游戏的 Steam 在线人数。
全部更新由 GitHub Actions 在云端完成，**不依赖任何人的电脑开机**。

## 它怎么工作

```
GitHub Actions 定时触发（每天 UTC 01:00 / 13:00，即北京 09:00 / 21:00）
   ├─ scripts/fetch_news.py       抓新闻（Google + Bing，自动译中）→ 更新 index.html
   ├─ scripts/fetch_linkedin.py   抓 Temu 官方 LinkedIn 帖（cookie 失效可跳过）
   ├─ scripts/fetch_steam.py      抓两款游戏 Steam 在线人数 → 更新 index.html
   ├─ scripts/fetch_youtube.py    抓 Temu 视频 + 热评 → 更新 index.html
   ├─ git commit + push（仅 index.html，页面无变化就跳过）
   └─ scripts/push_wechat.py      企业微信早报（仅早 9 点场次）
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
- **全网英文源**：Google 13 路 + Bing 14 路，共 27 路并发抓取。抓到的英文条目全部自动译成中文，页面中文标题占比长期接近 100%（2026-11-11 实测 449/449）。
- **不抓中文源**：Google News 的中文源博彩 SEO 站占比过高（实测 24 条里 15 条是垃圾），清洗成本远高于收益。
- **翻译走免费接口**：Google 公开翻译端点为主、MyMemory 为备，无需任何 API key。想保留英文原文加 `--no-translate`。
- **垃圾过滤**（必须做）：博彩/SEO 站会把广告词混进 Google News 中文源，实测「育碧」24 条里能有 15 条是这类垃圾。脚本内置关键词黑名单、来源黑名单、标题竖线数判定，以及 `'s Library` 这类个人频道噪声，自动丢弃。

### 翻译质量的三道保险

机器翻译直接套用会出不少洋相，所以加了几层处理：

1. **品牌名占位符保护** —— 翻译前把 Temu / PDD Holdings / Ubisoft / Rainbow Six 等 38 个专有名词换成占位符，译后还原。不这么做 Temu 会被音译成「特姆」「特木」。
   - 占位符必须带词边界 `(?<!\w)...(?!\w)`：否则 `Anno`（纪元这款游戏）会把 `announces` 切成 `QXnQXunces`，整句结构被打断，翻译接口就会乱翻。
2. **术语预替换** —— Trailer→预告片、Season Pass→赛季通行证、price target→目标价、year-on-year→同比 等 25 条。同样走占位符，否则译好的中文术语会被翻译接口二次处理（「免费游玩」曾被改成「免费站立」）。
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

### YouTube · Temu 视频速览

页面里 Steam 板块上方的「YouTube · Temu 视频速览」由 `fetch_youtube.py` 驱动：

```
YouTube Data API v3（需要免费的 API key，存仓库 Secret：YOUTUBE_API_KEY）
   ├─ search.list ×2     过去 48h 内的 Temu 视频（一路按播放量、一路按最新）
   ├─ videos.list        批量拉详情：时长 / 播放 / 点赞 / 评论数 / 描述
   └─ commentThreads ×N  每个视频的热门评论（relevance 前 20 条）
```

- **脚本侧总结不靠 AI 编造**：内容摘要 = 视频描述摘录（自动去掉链接、推广行）+ 章节列表；
  评论区小结 = 情绪词典统计（正面 / 负面 / 中性百分比）+ 高频主题词，全部是真实数据的统计或摘录。
- **AI 总结是会话侧产物**：仓库外的 WorkBuddy 自动化通读字幕全文后写入 `aiSummary`，
  页面按「AI 通读字幕 > 字幕摘句 > 视频描述」优先级显示并如实标注来源。
  云端脚本不产出 AI 总结，也**不会覆盖**已写入的 AI 总结（`update_youtube.py` 按来源等级继承）。
- **过滤**：时长 < 60 秒的 shorts 默认丢弃（`--min-duration` 可调），标题+描述须含 "Temu"。
- **配额**：每天约 210 units（搜索 200 + 详情 1 + 评论 8），免费额度 10000 units/天。
- **合并**：`update_youtube.py` 按 videoId 去重，新数据覆盖旧数据（但高级总结来源不会被低级来源降级），
  近 10 天内抓到过的视频保留在页面上，上限 **96 条**（`MAX_VIDEOS`）。数据没变化不改动文件。
- **没配 key 时的行为**：`fetch_youtube.py` 打印 `[SKIP]` 后 exit 0，不影响其他抓取步骤。
- **配置只需两步**：
  1. 到 [Google Cloud Console](https://console.cloud.google.com/) 新建项目 → 启用 **YouTube Data API v3** →
     凭据 → 创建 **API 密钥**（免费额度，无需绑卡）
  2. `gh secret set YOUTUBE_API_KEY --repo sword-runner-2100/news-hub --body "<API key>"`

## 目录结构

```
index.html                      页面本体（数据内联在 SEED / STEAM / YOUTUBE 三个标记块里）
scripts/
  fetch_news.py                 抓新闻（Google + Bing 双源，自动译中）
  fetch_linkedin.py             抓 Temu 官方 LinkedIn 帖（SDUI/RSC 解析，需 LI_AT）
  fetch_steam.py                抓 Steam 日度数据
  fetch_youtube.py              抓 Temu 视频 + 字幕 + 热评（需 YOUTUBE_API_KEY）
  update_news.py                把新闻合并进 index.html（去重、排序、备份、幂等）
  update_steam.py               把 Steam 数据合并进 index.html
  update_youtube.py             把视频合并进 index.html（总结来源优先级继承）
  push_wechat.py                企业微信群机器人早报（读 inbox/added.json）
  backfill_translate.py         把存量英文条目批量回译（幂等）
  dedupe_lib.py                 去重工具（精确键 + 2-gram 相似度），增量与存量共用
  dedupe_news.py                清洗存量重复条目（幂等）
  check_baseline.py             不可回退基线检查 / 自检 / 最小上下文包（只读）
.github/workflows/refresh.yml   定时任务（10 步）
```

数据在 HTML 里用标记块包裹。脚本按标记整段替换，**仅在数据确实变化时**递增 `DATA_VERSION`（空变化不写文件、不备份）：

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

脚本都是幂等的：数据没变化就不改动文件、不递增 `DATA_VERSION`、不产生提交，并给出提示。
`inbox/added.json` 按「同一抓取日累加、跨天重置」维护，避免 LinkedIn 那一步覆盖新闻步骤的新增，
导致早报漏发或重发旧条目。

## 抓取 LinkedIn 公司帖子（可选）

把 Temu 在 LinkedIn 发的帖子也收进汇总台。抓到的条目归入 `temu` 话题，
来源标 `LinkedIn`、分类标「官方」，不需要改页面结构。

**为什么必须配 cookie**：LinkedIn 未登录时拿不到任何帖子。实测——

| 尝试 | 结果 |
|---|---|
| 公司主页直接抓 | 只有粉丝数，帖子字段出现 0 次 |
| 帖子页 `/posts/` | 302 跳登录页 |
| RSSHub 官方实例 | 403（该路由需自托管配 cookie） |
| Bing `site:linkedin.com/...` | 0 条（搜索引擎不索引帖子） |
| Voyager 内部接口（voyager/api/...） | 全部 404 / 403，端点已下线 |

**解析方式（页面现在是 SDUI + RSC，不再是老 DOM）**

带 cookie 能拿到页面（4.8 MB，标题 "Temu: Posts"），但老的那套
`feed-shared-update-v2` DOM 已经一个都没有了：
`<code>` 标签 0 个、`permalink` 0 次、`createdAt` 0 次、可见文本里只有公司简介。
真正的数据在内嵌的 RSC 树里（组件状态用 `proto.sdui.State` protobuf 序列化）。

所以解析改成**按组件名定位**，不依赖任何 CSS 类名：

| 要什么 | 靠什么定位 |
|---|---|
| 正文 | `viewName":"feed-commentary"`，正文是里面的字符串字面量 |
| 发布时间 | `viewName":"feed-full-update"`，其后紧跟 `1d` / `2d` 这类相对时间 |
| 永久链接 | `postSlugUrl":"https://www.linkedin.com/posts/..."` |

两个坑，代码里都处理了：

- **正文被切成四种形态**：`{"children":[null,"一句话"]}`、
  换行后的 `{"children":[["$","br",null,{}],"一句话"]}`、
  中间夹 @提及/链接的 `[null,"前半句",[...]]`（结尾也可能是 `,null]`）、
  以及被加粗链出去的机构名 `{"children":["ICQRF"]}`。
  少抓任何一种都会丢掉帖子第一句。同一种模式按位置排序后拼接，
  撞上第一句就停（同一条帖子会被连续渲染两遍）。
- **链接和正文对不上号**：`postSlugUrl` 在文档里的位置跟正文顺序不一致，
  不能按下标配对。但 slug 本身是由正文前几个词生成的
  （`temu-has-signed-of-a-memorandum-of-understanding-...`），
  所以按「slug 词序列 ∩ 正文前缀」的最长公共前缀做贪心分配即可，3 条全部对上。

抓到的英文帖同样走 `fetch_news.py` 的翻译链路（品牌名占位符 + 术语表）再上页面。

**配置：**

1. 浏览器登录 linkedin.com（**建议用小号**，自动化访问违反 LinkedIn 用户协议，主号有风险）
2. F12 → Application（应用）→ Storage → Cookies → `https://www.linkedin.com`
3. 复制 `li_at` 的 Value
4. 存进仓库：

```bash
gh secret set LI_AT --repo <用户名>/<仓库名> --body "<复制的值>"
```

**没配置时**：脚本静默跳过，不影响新闻抓取。

**cookie 会过期**（几个月到一年）。失效时 LinkedIn 会回一个 `li_at=delete me`
并把请求 302 回原地址，脚本据此明确报「登录态失效」，重新取一次即可。
这一步在 workflow 里标了 `continue-on-error`，即使失效也不影响新闻和 Steam 的更新。

想换公司：改 `fetch_linkedin.py` 里的 `COMPANY`（默认 `temuapp`），
或设环境变量 `LI_COMPANY`。

## 推送到微信（可选）

有两条路，互不冲突：

**路 A：WorkBuddy 云端自动化（每天 9:20）**

自动化「news-hub · 推送当天网页新闻摘要」会去读线上页面，把当天新增条目
按板块整理成中文摘要输出。WorkBuddy 侧已连的微信只能**读**（有读会话/读消息
接口，没有发送接口），所以这是唯一能流到微信的路子。
不需要在仓库里配任何密钥。

**路 B：企业微信群机器人（GitHub Actions 里推送）**

每天早 9 点那次 workflow 把当天新增的新闻 POST 到企业微信群。晚 21 点只刷数据，不推送。

**配置只需三步：**

1. 企业微信里建一个群（拉一个人进来，或用内部群）→ 群设置 → 群机器人 → 添加机器人 → 复制 Webhook 地址
   （形如 `https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxxxx`）
2. 仓库 **Settings → Secrets and variables → Actions → New repository secret**
3. Name 填 `WECHAT_WEBHOOK`，Value 粘贴上面的地址，保存

也可以一条命令搞定：

```bash
gh secret set WECHAT_WEBHOOK --repo <用户名>/<仓库名> --body "<Webhook 地址>"
```

**没配置时的行为**：脚本检测到没有 `WECHAT_WEBHOOK` 就静默跳过，不影响抓取和提交。
所以你可以先跑通抓取，回头再配推送。

推送内容是企业微信 markdown：按话题分组，每条带标题链接、一句话摘要、来源与分类，
末尾附 Steam 在线人数。正文超 3800 字节会按整条丢弃（不把新闻截成半句）。

**想换成别的服务**（Server酱 / PushPlus / 钉钉等）：改 `scripts/push_wechat.py` 的
`build_content()`（消息正文）和 `send()`（POST 地址与请求体）两个函数即可，
其余流程不用动。

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

## 改动前先跑回归检查

页面把 449 条新闻、81 条视频和 Steam 数据全部内联在 `index.html` 里（数据占约 86%），
纯逻辑只占几百行。任何重构前先跑：

```bash
python3 scripts/check_baseline.py --self-test   # 38 项不变量 + 5 项「故意改坏」自检
python3 scripts/check_baseline.py --map         # 输出不含数据的逻辑骨架，给模型当固定上下文
```

覆盖：三个标记块、`DATA_VERSION`、localStorage 键与 STATE 五字段、话题枚举、AppID、
去重阈值 0.45、官方帖免去重、官方徽章、`loadItems` 补新 / `noReseed` / 复合键防 id 碰撞、
09:00 / 21:00 排期、导入导出与清空二次确认、AI 总结优先级、幂等语义。
脚本只读、零依赖，**不挂在 Actions 上**，避免误报阻断数据刷新。

> 运行时不引入任何付费 LLM / 新密钥。Hy4 这类模型只在**会话侧改代码**和**离线内容审阅**环节使用，
> 定时抓取的执行体始终是 GitHub Actions。

## 已知限制

- **翻译非 AI**：走免费机器翻译接口，偶尔会有生硬或轻微误译（尤其是双关语）。原文链接始终保留，可点开核对。
- **YouTube 内容总结分三档**：AI 通读字幕总结（仓库外自动化写入，基于字幕全文）> 字幕摘句（带时间戳可回溯）>
  视频描述摘录；卡片标签会如实标注来源，评论区小结是统计结果而非逐条人工阅读。想看完整内容点卡片进原视频。
- **字幕在 Actions 上常被拦**：数据中心 IP 抓不到字幕，字幕总结主要靠本地 Mac 抓取后提交，
  或由外部自动化补写；云端无字幕时按既有降级链处理。
- **历史 id 碰撞**：早期 id 由截断后的 URL 生成，Bing 链接前 60 字符相同，现存 4 组共 9 条共享 id。
  新条目已改为「截断名 + 完整 URL 的 8 位哈希」，页面合并改用 `id + url` 复合键，刷新不再丢条目；
  这批历史数据的已读 / 星标状态仍会联动（不改动旧 id 是为了不丢用户状态）。
- **链接**：Google 源的条目是 `news.google.com` 中转地址，浏览器点击会自动跳转到原文，但不是原文直链。Bing 源的条目已解析成真实直链。
- **摘要覆盖率**：只有 Bing 源给摘要，所以约一半条目有摘要，其余只有标题。
- **Actions 推送冲突**：如果本地也改了 `index.html`，推送前记得先 `git pull --rebase`，因为 Actions 会往同一个分支提交。
