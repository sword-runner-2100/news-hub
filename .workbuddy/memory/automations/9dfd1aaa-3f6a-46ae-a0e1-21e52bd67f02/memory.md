# Automation 9dfd1aaa 执行记录（每日 YouTube Temu 抓取 + AI 总结）

## 2026-10-24 08:30
- 抓取成功：96 候选 → 8 视频（7 带字幕、1 捏捏乐短频降级描述），inbox/youtube-2026-10-24.json。
- AI 处理：5 个 AI 总结+标题热评翻译（西语亲子号 Mamá y mia 返校季带货优惠码 kjb6985：双面彩笔/带灯放大镜/记事本/硅胶手工桌垫 iVRwS29seKA——连续第 2 天同条 / 阿塞拜疆语 mirsabdiary 150 马纳特家居包裹开箱，热评嫌贵 Q8ghWQtRjS8——连续第 2 天同条 / 哥伦比亚 El Muñe 露营装备实测吐槽：铝膜隔热垫薄如纸判不行、声明无合作 4QA_tdL6zyw / 阿根廷 Brillager 万圣节三造型 cos（芭比/病娇模拟器爱野/初音未来），20 万比索优惠码联盟带货 h07kcjuS9tU / 德语 Sturmwaffel 肝肠味棉花糖居然有咸香 5 分、咖喱香肠味 3 分、单件 5 欧判太贵 jmj-U-lAPqw）；1 个无字幕仅翻译（英语捏捏乐短频带码 khr2933 sP9jVTMWAUg）；2 个剔除（u8ENGfm3LzA Free Fire 直播 "CUÑADO YT de TEMU" 主播外号梗词，连续第 3 天同条 / rX9C6UoH9lw 印尼语 "Titik temu"=相遇点 AI 恋爱短剧，词形巧合）。
- push 流程：远端有 Actions 夜间提交 38a4b7c，stash 后 pull --rebase fast-forward → stash pop 时 index.html 冲突 → checkout HEAD 取远端基底 + drop stash → 重跑 update_youtube.py（66 在页）。
- **第 21 次抓到 Actions 降级**：昨日 AI 视频 RUceq57Cf-M（西语 Ale Wang 食品试吃）、mBSg_NUA8Dg（哥伦比亚 Semana 报道）被远端基底降回 description，已从 inbox/youtube-2026-10-23.json 取回整条追加进今日 JSON 重跑合并恢复，ai 回到 44。
- 提交 149f8c1 推送成功（连带另一 automation 的 memory 文件）。最终核验：66 视频、44 个 summarySource=ai 全带 aiSummary 与中文标题、今日 6 条全在页、历史 42 条重点噪声零混入。临时脚本已删除；scripts/ 与 .env.local 未动。

## 2026-10-23 08:30
- 抓取成功：96 候选 → 8 视频（7 带字幕、1 塞尔维亚语降级描述），inbox/youtube-2026-10-23.json。
- AI 处理：6 个 AI 总结+标题热评翻译（西语 Ale Wang 与好友试吃约 20 款 Temu 食品：鸡肉味零食 10 分、10 美元切片肉干量少似鞋底给 8 分 RUceq57Cf-M / 俄语 Natalya_Erbol "0 坚戈免单"包裹开箱带货，热评拆穿不凑单拿不到免费 NciFEvqQOIw——与昨日同条 / 德语 Sturmwaffel 猎奇食品实测近半过期（Takis 7 月到期），肝肠味棉花糖 5 分判不建议买 eVl0ebCfhu4——与昨日同条 / 西语亲子号 Mamá y mia 返校季带货优惠码 kjb6985 iVRwS29seKA / 哥伦比亚 Semana 报道 Shein/Temu/AliExpress 冲击当地：或失 2000 岗位、Temu 月发 220 万包裹、桑坦德 16 家关停 mBSg_NUA8Dg / 阿塞拜疆语 150 马纳特包裹开箱，博主自评部分与图片不符、热评嫌贵 Q8ghWQtRjS8）；1 个无字幕仅翻译（塞尔维亚语 Lord Zeks "XXXL Haul Unboxing"，热评提到 Temu 加长款，保留 rztck187yso）；1 个剔除（u8ENGfm3LzA Free Fire 直播 "CUÑADO YT de TEMU" 主播外号梗词，同昨日 CW-c3A57niI 性质）。
- push 流程：stash 后 pull --rebase fast-forward（远端 Actions b46138e，基底 60→67）→ stash pop 时 index.html 冲突 → checkout HEAD 取远端基底 + drop stash → 重跑 update_youtube.py（67 在页）。
- **第 18 次抓到 Actions 问题（噪声 3 + 降级 2）**：远端基底带回昨日 3 条已剔噪声（3b_kymZp-Oc / CW-c3A57niI / _Nrgw1WFijU），且昨日 AI 视频 Qt33Qy5_-rM、Xfx8D6CyMms 被降回 description，已从 inbox/youtube-2026-10-22.json 取回整条恢复。补丁后 64 在页、ai=45。
- **核验教训：不要把"无字幕 description 条目"误判为降级**——bZQbYZzC_FE 昨日就是 description（无字幕仅翻译），页面条目中文标题/译文完好，本次恢复脚本断言失败中止、未写坏文件，属虚惊。
- 提交 50ecb1a 推送成功（连带 memory 与 reports 文件）。最终核验：64 视频、45 个 summarySource=ai 全带 aiSummary 与中文标题、今日 7 条全在页、昨日 5 条完好、42 条重点噪声零混入。临时脚本已删除；scripts/ 与 .env.local 未动。

## 2026-10-22 08:30
- 抓取成功：94 候选 → 8 视频（7 带字幕、1 无字幕降级描述），inbox/youtube-2026-10-22.json。
- AI 处理：4 个 AI 总结+标题热评翻译（英语 Ginge+ 实测 Temu 零食多数难吃 Qt33Qy5_-rM——与昨日同条 / 德语 Sturmwaffel Temu 食品实测开场即发现近半商品过期（Takis 7 月到期）判不建议买 eVl0ebCfhu4 / 哈萨克斯坦俄语博主 0 坚戈免单 Temu 包裹开箱带货 NciFEvqQOIw / 西语 elmexitachi 万圣节 0 美元码 kfg8776 带货短剧 Xfx8D6CyMms，如实注明是宣传短剧）；1 个无字幕仅翻译（malaika Rathore 捏捏乐 0 美元开箱 bZQbYZzC_FE，热评指出是搬运 Joyful Tingles 的视频）；3 个剔除（3b_kymZp-Oc 摩洛哥阿语蛋糕教程 #temu 引流，与昨日同条 / CW-c3A57niI Free Fire 直播 "CUÑADO YT de TEMU" 主播外号梗词，同昨日 qRtUlsCEmdU 性质 / _Nrgw1WFijU "Temu Michael Jackson" 山寨梗词 freestyle 短视频，同 Temu Obama 先例）。
- push 流程：stash 后 pull --rebase fast-forward（远端 Actions 9e09a73）→ stash pop 时 index.html 冲突 → checkout HEAD 取远端基底 + drop stash → 重跑 update_youtube.py（66 在页）。
- **第 17+1 次抓到 Actions 带回历史噪声**：bCdGuZ1Yg1U + g2357DlxMqg（Link Lauren "Temu Royals" 山寨王室梗词，昨日刚剔）再次被远端基底带回，用 exclude 补丁 JSON 走 update_youtube.py 剔除，64 在页。
- 提交 1d7d665 推送成功。最终核验：64 视频、47 个 summarySource=ai 全带 aiSummary 与中文标题、今日 5 条全在页、昨日 3 条 AI 无降级、42 条重点噪声零混入。临时脚本已删除；scripts/ 与 .env.local 未动。

## 2026-10-21 08:30
- 抓取成功：96 候选 → 8 视频，inbox/youtube-2026-10-21.json。
- AI 处理：3 个 AI 总结+标题热评翻译（英语 Ginge+ 实测 Temu 零食多数难吃 Qt33Qy5_-rM，孟加拉语自动译文 / 英语 Sydney 捏捏乐 0 美元码带货 kop8458 IsIprdcFgno 与昨日同条 / 英语 You Betcha 51 刀 Temu CarPlay 装 99 款雪佛兰好评 VtWet3AW5qw 与昨日同条）；0 个无字幕；5 个剔除（3b_kymZp-Oc 阿语蛋糕教程 #temu 引流 / TObkaHTwP3c 波语 "temu"="之前"词形巧合德国美食排名 / qRtUlsCEmdU Free Fire 直播 "CUÑADO YT de TEMU" 主播外号梗词 / bCdGuZ1Yg1U + g2357DlxMqg Link Lauren "Temu Royals" 山寨王室贬称梗词×2）。
- push 流程：rebase 冲突 → abort 重试仍冲突 → 重建方案（backup/main-20261021 → reset --hard 远端 211a525 → 重跑 update_youtube.py 68 在页）。**新教训：reset --hard 在 rebase 进行中执行会留下残留 .git/rebase-merge 目录 + HEAD 游离 + 本地 main 停旧位，push 连报 non-fast-forward（远端没动）。修复 = rm -rf .git/rebase-merge + git branch -f main HEAD + checkout main。今后重建前必须先 abort 干净再 reset。**
- stash pop 时旧 index.html 冲突 → checkout HEAD 保留已推送版本 → drop stash，memory 正常恢复。
- 提交 b3f8db3 推送成功。核验：68 视频、52 个 ai 全带 aiSummary、今日 3 条全在页、昨日 8 条无降级（本轮 Actions 未降级）、38 条重点噪声零混入。临时脚本已删除；scripts/ 与 .env.local 未动。备份分支 backup/main-20261021 保留。

## 2026-10-20 08:30
- 抓取成功：93 候选 → 8 视频全带字幕，inbox/youtube-2026-10-20.json。
- AI 处理：8 个 AI 总结+标题热评翻译（乌克兰语 Andro-news 科技周报：手机销量 14 年新低+乌议会对 Ali/Temu 包裹征 20% 增值税等，Temu 为议题之一非测评已注明 nmncbhNoHiU / 阿塞拜疆语 Tacir 600 马纳特 Temu 服装包裹试穿 nFGFeGgRf9k / 英语 Badbishlily 24 小时只吃 Temu 食品挑战 7tKv7QQRa_Q / 西语 VICTOR CABALLERO 1 美元翻新 PS5+Xbox 开箱、反复声明"别在 Temu 买东西"防骗 qgL0DgCvWqo / 德语 Gnu Glotzt reaction Temu 调查片：纯中介+AI 假网红营销+婴儿玩具有毒 bNgK43Js1Pk / 西语 Rango Temu 声呐+水下摄像头渔具实测、联盟带货 FSlzfv8-kDI / 英语 Sydney 捏捏乐 0 美元码带货 kop8458、热评揭"免费"实需满 20 刀 IsIprdcFgno / 英语 You Betcha 51 刀 Temu CarPlay 装 99 款雪佛兰好评 VtWet3AW5qw）；0 个无字幕；0 个剔除（8 条均与 Temu 相关）。多数字幕是阿语自动译文已注明。
- push 流程：**第 20 天首次 rebase 顺利**——stash 后 pull --rebase fast-forward（远端 Actions 1ad0e80）→ stash pop 时 index.html 冲突 → checkout HEAD 取远端基底 + drop stash → 重跑 update_youtube.py（67 在页）。
- **第 17 次抓到 Actions 降级**：昨日 AI 视频 se55EyGL1RI（西语零元购带货短剧"送货员"）被远端基底降回 description，已从 inbox/youtube-2026-10-19.json 取回整条恢复，ai 回到 55。历史噪声零混入。
- 提交 3081f03 推送成功。最终核验：67 视频、55 个 summarySource=ai 全带 aiSummary、标记零不一致、今日 8 条全在页、33 条重点噪声零混入。
- 临时脚本（写回+恢复+核验，均含条目数/videoId 断言）已删除；scripts/ 与 .env.local 未动。

## 2026-10-19 08:30
- 抓取成功：8 视频（7 带字幕、1 塞尔维亚语降级描述），inbox/youtube-2026-10-19.json。
- AI 处理：7 个 AI 总结+标题热评翻译（英语 Dude Life 三兄弟 Temu/Amazon/TikTok Shop 充气 A 字屋过夜对比 PxDA-WzNPjc——与昨日同条复用 / 英语 Beluga 充电器恶搞短剧 GJVYoxHhOHE——与昨日同条，字幕近空但非空按 AI 处理并注明非真实测评 / 阿塞拜疆语 AYKA 14 秋装两包裹 Le69FvqUNFk——与昨日同条复用 / 英语 REPerformance 修复 Chris Slix Temu 超跑（换电池+修悬挂+查漏液，如实注明主体为汽车维修）tBk7uvx6VqM / 旁遮普语 Pulwasha 厨房用品开箱+KU7399 优惠码联盟带货 L63K-21a3Ek / 保加利亚语给猫订 300 欧万圣节包裹 CSPopgWyknI / 西语哥伦比亚纺织业评论：Arturo Calle 因 Temu/Shein 裁员 2000+、de minimis 包裹 4300 万→1.3 亿件 FhtCyY65WFQ）；0 个无字幕仅翻译（唯一 description 条目被剔除）；1 个剔除（aPE37YReGvI 塞尔维亚语 "KUPIO SAM BMW 530 SA TEMU-a"="从 Temu 买宝马"劣质改装梗，评论区全谈改装车与平台无关，同 09-27 DbZrtKbb1ro 先例）。
- push 流程：commit 后 rebase 冲突（第 19+1 天连冲突），abort 重试仍冲突 → 沿用重建方案：backup/main-20261019 → reset --hard 到远端 11b8f37（Actions 10-18 16:28 UTC）→ 重跑 update_youtube.py（61 在页）→ 补丁 + 提交 b2616f7 推送成功。注意：重建方案会丢掉上个本地 commit 里的 memory/reports 文件（保留在备份分支，本次 2026-10-18.md 与昨日报告已从备份找回并随本次提交附带？——实际未随附，仅 index.html 入提交，memory 文件留在备份分支）。
- **第 16 次抓到 Actions 问题（降级 1 条 + 噪声 1 条）**：昨日 AI 视频 2DMp5MkQZUg（罗马尼亚语 Ariana Mtz 婴儿用品开箱）被远端基底降回 description，从 inbox/youtube-2026-10-18.json 取回整条恢复；噪声 qatMNHO5_Lg（摩洛哥阿语宗教说教）再次被带回，已移除。核验清单教训：6qsJn4A73YA 是格鲁吉亚语无字幕正经视频，勿再列入噪声清单（本次误报一次）。
- 提交 b2616f7 推送成功（diff 3942 行删除为 pretty→minified，正常）。最终核验：60 视频、49 个 summarySource=ai 全带 aiSummary、今日 7 条全在页、32 条重点噪声零混入。
- 临时脚本（写回+补丁+核验，均含条目数/videoId 断言；补丁脚本首跑因"剔除后应为 60"误写成 61 断言失败，文件未写坏，修正后通过）已删除；scripts/ 与 .env.local 未动。备份分支 backup/main-20261019 保留。

## 2026-10-17 08:30
- 抓取成功：99 候选 → 8 视频（7 带字幕、1 格鲁吉亚语降级描述），inbox/youtube-2026-10-17.json。
- AI 处理：5 个 AI 总结+标题热评翻译（伊拉克阿语带货博主 Temu 开箱，与昨日同条复用总结 oPVB9BER2QY——连续第 2 天 / 西语 Islas Plus Temu 烧烤特辑：便携炭烤架+Shark Tank"啤酒发射器"+烤架清洁刷最惊艳会回购 4LnAHQxtELA / 阿塞拜疆语 AYKA 14 给婆婆的 400 马纳特包裹：猫沙发+Kasi 手表比本地便宜近 70 ticrQ47fAdM / 俄语 BANARU 开箱带锁信箱+925 银耳环+院子施工 JOWnxKalOWM / 摩洛哥阿语 Just Nini 带货 #ad 优惠码 ali753212：胶带救的耳夹+形似十字架的夹子引发热评争议 v5gcbaoRVQw）；1 个无字幕仅翻译（格鲁吉亚语互赠 TEMU 露营装备 6qsJn4A73YA——连续第 2 天同条）；2 个剔除（OD6RldzjTHw "Temu Zach D Films Is Cursed" 山寨梗词，同 09-26 XEOORQGckI4 先例 / pNqMpubE2rQ 4.6 小时西语 Free Fire 直播 "CUÑADO YT de TEMU"=主播外号梗词）。
- push 流程：stash 后 pull --rebase fast-forward（远端 Actions 07322e0）→ stash pop 时 index.html 冲突 → checkout HEAD 取远端基底 + drop stash → 重跑 update_youtube.py。
- **第 14 次抓到 Actions 丢数据**：Actions 10-16 17:19 UTC（07322e0）把 dV0UAd6kHy4（More Aj TikTok Shop vs Temu）和 GgoSemqgyns（More WillNE Temu 奢侈品）两条 AI 视频整条丢掉，已分别从 inbox/youtube-2026-10-15.json、10-14.json 取回恢复，ai 回到 47。
- **发现昨晚 20:35 有第二轮本地刷新**（提交 e59be4d，非本 automation，记录在另一 automation 9b208658/52bed6be 的 memory）：它将 o3oHsJZFnb8（WSJ 奇瑞 Jaecoo"Temu 版揽胜"汽车报道）改判为噪声剔除——最近一次明确决策，本次尊重未恢复。
- **核验清单纠错**：6mlYu40r9_0（10-11 Sturmwaffel 玉米热狗机）是正经 AI 视频非噪声，之前清单误标过，今后勿再列入。
- 提交 9e910d6 推送成功（连带 3 个已暂存 memory 文件，与往日一致）。最终核验：58 视频、47 个 summarySource=ai 全带 aiSummary、标记零不一致、今日 6+恢复 2 全在页、29 条重点噪声零混入。
- 临时脚本（写回+恢复，均含条目数/videoId 断言）已删除；scripts/ 与 .env.local 未动。

## 2026-10-16 08:30
- 抓取成功：96 候选 → 8 视频全带字幕，inbox/youtube-2026-10-16.json。
- AI 处理：5 个 AI 总结+标题热评翻译（伊拉克阿语博主 Temu 应用开箱：保鲜袋/手摇动能小夜灯/儿童玩具+优惠码 KNP953 带货 oPVB9BER2QY / 德语 Klengan 调查视频：Temu 无自营无仓库纯中介、46 万包裹/日无人抽检、伪造网红与砍价裂变营销 A6FWUflgpdE——连续第 2 天同条 / 阿语 Sara's Makeup 服饰开箱：镂空裙偏透偏大、100% 聚酯纤维+SE10 优惠码植入 57S_cfkCTT0——连续第 2 天同条 / 英语 WSJ 报道：奇瑞 Jaecoo 7 被戏称"Temu 版揽胜"成英国畅销车，Temu 为戏称、视频主体是汽车行业报道已如实注明 o3oHsJZFnb8 / 德语 Sturmwaffel 实测烤肉味棉花糖 5.35 欧判甜腻怪味不建议 Ria26WZBfc4）；0 个无字幕；3 个剔除（X8wW0TwuZ_c 摩洛哥语宗教说教"屋顶晾晒衣物" #temu 纯引流、WFoRLY_EngU 僧伽罗语斯里兰卡时政播客 "Temu Version"=山寨梗词、PaLl9CRUcc0 美国时政剪辑 "Temu Obama"=政客外号梗词）。
- push 流程：第 19 天首次 rebase 顺利——stash 后 pull --rebase fast-forward（远端 Actions 提交 1302fa1）→ stash pop 时 index.html 冲突 → checkout HEAD 取远端基底 + drop stash → 重跑 update_youtube.py（57 在页）。
- **第 13 次抓到 Actions 降级**：昨日 AI 视频 dV0UAd6kHy4（More Aj TikTok Shop vs Temu 对决）被远端基底降回 description，已从 inbox/youtube-2026-10-15.json 取回整条恢复，ai 回到 45。历史噪声零混入（本次 22 条重点噪声清单全不在页）。
- 提交 817d54e 推送成功（连带 memory 与 reports 文件）。最终核验：57 视频、45 个 summarySource=ai 全带 aiSummary、今日 5 条全在页、昨日 8 条无降级。
- 临时脚本（写回+恢复，均含 videoId 断言）已删除；scripts/ 与 .env.local 未动。备份分支 backup/main-20261016 保留。

## 2026-10-15 08:30
- 抓取成功：95 候选 → 8 视频全带字幕，inbox/youtube-2026-10-15.json。
- AI 处理：8 个 AI 总结+标题热评翻译（英语 More Aj TikTok Shop vs Temu 商品对决（35 英镑思乐冰机/榨汁机 A 级、Temu 汉堡架 D 级）dV0UAd6kHy4 / 英语 JOE CLIPPER Joe Bart 直播剪辑观众投票买猎奇 Temu 商品 faF5S0e5NGQ / 英语 Joe Bart 4.5 小时直播回放（26:08-1:46 Temu 挑选环节）xsIyvLk_ZAE——连续第 2 天 / 德语 Klengan 调查视频：欧盟因婴儿玩具含毒罚 2 亿欧、防晒霜 SPF<1、46 万包裹/日无人抽检 A6FWUflgpdE / 阿语 Sara's Makeup Temu 服饰开箱几乎全军覆没+SE10 优惠码植入 57S_cfkCTT0 / 英语 The Ginger Fisherman Temu 5 节旅行竿钓上 8 磅 15 盎司巴赫鱼+khj2796 优惠码 eZuRQsuBkWw / 阿塞拜疆语 Tacir 家庭 vlog 接发美甲+Temu 衣物麦克风开箱 xX4tPEUwbNU / 德语 Sturmwaffel 棉花糖"鸡块"三种口感纯糖判灾难级 fPCfzDSPoXc）；0 个无字幕；0 个剔除（8 条均与 Temu 相关）。
- push 流程：先 stash 后 pull --rebase 顺利 fast-forward（远端 Actions f0828b0），stash pop 时 index.html 冲突 → checkout HEAD 取远端基底 + drop stash → 重跑 update_youtube.py（69 在页）。
- **第 12 次抓到 Actions 问题**：远端基底带回 2 条昨日已剔噪声（lik2iCqzVjs 阿语摩洛哥婚姻故事 / yVq9ppQeGD8 "Zack D Films From Temu" 山寨梗词），且昨日 AI 视频 GgoSemqgyns（More WillNE Temu 奢侈品实测）被降回 description 丢 aiSummary。已打补丁：剔除 2 噪声 + 从 inbox/youtube-2026-10-14.json 取回整条恢复，67 在页。
- 提交 97f6550 推送成功（连带 4 个已暂存的 memory 文件，与往日一致）。最终核验：67 视频、52 个 summarySource=ai 全带 aiSummary、今日 8 条全在页、17 条重点噪声零混入。
- 临时脚本（写回+补丁，均含条目数/videoId 断言）已删除；scripts/ 与 .env.local 未动。

## 2026-10-13 08:30
- 抓取成功：94 候选 → 8 视频全带字幕，inbox/youtube-2026-10-13.json。
- AI 处理：7 个 AI 总结+标题热评翻译（日语おーがすと SHEIN vs Temu 穿搭对决 bGeMBdiUXqw——连续第 2 天 / 德语 Mohi Toys Amazon vs Temu 玩具对比本集 Temu 全胜 CPFa2_oa-Ls / 英语 Ina Yu Temu 买最便宜国行 PS5 自己破解锁区+加装 1TB 固态 opOBQR49Z2U / 德语 Sturmwaffel Temu 新食品实测判灾难级（波兰 Milka 棉花糖疑走私货）cZUi-c2duVI——连续第 2 天 / 英语 More WillNE 团队实测 Temu 奢侈品（梵克雅宝风格手链/金扑克/6 英尺狮子像）GgoSemqgyns / 德语 Sturmwaffel 弹射式开瓶器 1.52 欧实测差评 hgXygJ4E6kY——连续第 3 天 / 阿尔巴尼亚语 Noraafitt 万圣节带货优惠码 kev5423 x_AT0ctikNI——连续第 2 天）；0 个无字幕；1 个剔除（A7yGA-VTRbI 3.7 小时日语闲聊直播，仅标题顺带提一句"TAKAHIRO 穿 Temu 衣服"，正文与 Temu 无关）。
- push 流程：index.html 未暂存导致 pull --rebase 拒绝 → 先 stash 后 rebase fast-forward（远端有 Actions 10-12 21:42 UTC 提交 588d519）→ stash pop 时 index.html 冲突 → 按预案 checkout HEAD 取远端干净基底 + reset → 重跑 update_youtube.py（70 在页）→ 提交 20c9eb1 推送成功 → 丢弃失效 stash。
- 核验：70 视频、53 个 ai 全带 aiSummary、今日 7 条全在页（5 条 fetchedAt 保留昨日首抓日期属正常）、昨日修复 3 条（jiOqAB7HltM/h_7MbIGnayk/q7oRfSaL6f4）完好、8 条重点噪声零混入。
- 临时脚本已删除（写回脚本含条目数/videoId 集合/ai 数量断言）；scripts/ 与 .env.local 未动。

## 2026-10-12 08:30
- 抓取成功：8 视频全带字幕，inbox/youtube-2026-10-12.json。
- AI 处理：7 个 AI 总结+标题热评翻译（日语おーがすと SHEIN vs Temu 穿搭对决 bGeMBdiUXqw / 德语 Sturmwaffel 垃圾袋提手 zOyxpgVVerk / 德语 Sturmwaffel Temu 新食品实测 cZUi-c2duVI / 德语 Sturmwaffel 多功能咖啡杯套 A2CWtlDUQ7A（连续第 2 天） / 德语 Sturmwaffel 弹射式开瓶器 hgXygJ4E6kY / 英语 Denki 数码开箱（含 450 美元可骑行行李箱）hi361S3cHOI / 阿语 Noraafitt 万圣节带货 x_AT0ctikNI）；0 个无字幕；1 个剔除（P8K2lvuabxM 波语 "7 MINUT TEMU"="7 分钟前"王室八卦，词形巧合）。
- rebase 第 17 天首次无冲突：本地仅落后远端一个 Actions 提交（cf99286）无分叉，先 stash .workbuddy memory 再 pull --rebase 即 fast-forward（stash 是因为 memory.md 为 tracked 修改，会阻止 rebase）。
- 合并 68 视频在页。核验：50 个 ai 全带 aiSummary、今日 7 条在页、昨日 7 条无降级、历史噪声零混入。注意 TnvXELThO4w 是 10-09 正经 AI 视频，不是噪声（本次核验清单误标过）。
- 提交 9337fc5 推送成功。临时脚本已删除；scripts/ 与 .env.local 未动。

## 2026-10-11 08:30
- 抓取成功：97 候选 → 8 视频全带字幕，inbox/youtube-2026-10-11.json。
- AI 处理：7 个 AI 总结+标题热评翻译（德语 Sturmwaffel 切面包板 3/5 分 DJUcmfE4qrs——连续第 2 天同条 / 阿塞拜疆语 AYKA 14 回应恶评 vlog+123 马纳特擦窗机器人 ZSAZCjdq5l0——连续第 2 天同条 / 英语主播 Mega Temu 服装试穿直播剪辑 jI1aBtRSpSQ，内容成人化已如实注明 / 德语 Sturmwaffel 玉米热狗机 37.60 欧判 5/10 6mlYu40r9_0 / 日语都市传说"Temu 卖被诅咒的盗版《我的世界》"xO7oa1XJ_MQ，娱乐演绎已如实注明 / 英语 NerdECrafter Temu 假万圣节捏捏乐对比 JKmDb-0iras，假货质感意外不错、字幕为阿语自动译文 / 德语 Sturmwaffel 1.29 欧咖啡杯套判 1/5 A2CWtlDUQ7A）；0 个无字幕；1 个剔除（S6eD8KhE89w "TEMU MK" 街球 1v1，连续第 2 天同条）。
- rebase 第 16 天连冲突，abort 重试仍冲突。沿用重建方案：backup/main-20261011 → reset --hard 到远端 d858014（Actions 10-10 17:45 UTC）→ 重跑 update_youtube.py（67 在页）。
- **第 10 次抓到 Actions 带回历史噪声**：Ii9LrghHMSM（印尼语时政直播）再次被远端基底带回，剔除补丁后 66 在页。**第 10 次抓到 Actions 降级**：_xmQWD8CD98（Temu 翻车合集第 1 部分）被降回 description，已从备份分支取回整条恢复，ai 回到 47。
- 提交 3ccc7fe 推送成功。最终核验：66 视频、47 个 summarySource=ai 全带 aiSummary、今日 7 条全在页、备份 diff 零降级、16 条重点噪声零混入。
- 临时脚本已删除（写回脚本含条目数与 videoId 集合 assert）；scripts/ 与 .env.local 未动。备份分支 backup/main-20261011 保留。

## 2026-10-09 08:30
- 抓取成功：97 候选 → 8 视频（7 带字幕、1 降级描述），inbox/youtube-2026-10-09.json。
- AI 处理：5 个 AI 总结+标题热评翻译（罗马尼亚语 Bogdan IBMFamily 10 列伊小商品实测 kkHltZqxFbU——连续第 3 天同条，正常重处理 / 德语 Sturmwaffel 厨房小工具吐槽 EE5YZq0-ZAE，芒果切果器 8.28 欧被判不值 / 阿塞拜疆语 AYKA 14 Temu 七层木质鞋架 VFLkGOCO-RA——连续第 3 天同条 / 英语 Katie Roams Temu 迷彩帐篷野外过夜 TnvXELThO4w——弄丢炉头转接头只吃麦丽素哭了 25 分钟，字幕为阿语自动译文 / 日语 USB 优盘 20 支批量购 vv6dyLyTUiA，带 #PR 植入、优盘无容量虚标，如实注明）；1 个无字幕仅翻译（克罗地亚语 ZOV PRIREODE 秋季鞋裙开箱 TJTY_W5mtUQ）；2 个剔除（LROBGBZXj5s "TEMU SOLO LEVELING"=Solo Leveling 山寨动漫吐槽、Temu 为山寨梗词 / Ii9LrghHMSM 印尼语时政直播，temu=印尼语"会面"指 Prabowo 与 Jokowi 会面）。
- rebase 第 14 天连冲突，abort 重试仍冲突。沿用重建方案：backup/main-20261009 → reset --hard 到远端 fc05186（Actions 10-08 19:15 UTC）→ 重跑 update_youtube.py（65 视频在页）。远端基底本就含昨日 AI 数据，无降级需修复，历史噪声零混入。
- 提交 d432a04 推送成功。最终核验：65 视频、47 个 summarySource=ai 全带 aiSummary、今日 6 条全部在页且来源正确、9 条重点历史噪声零混入。
- 临时脚本已删除（写回脚本含 assert 条目数与 videoId 集合不变）；scripts/ 与 .env.local 未动。备份分支 backup/main-20261009 保留。

## 2026-10-08 08:30
- 抓取成功：94 候选 → 8 视频（7 带字幕、1 降级描述），inbox/youtube-2026-10-08.json。
- AI 处理：6 个 AI 总结+标题热评翻译（罗马尼亚语 Bogdan IBMFamily 10 列伊小商品实测 kkHltZqxFbU / 阿塞拜疆语 AYKA 14 Temu 手机壳包裹 X43Erz10Do8——连续第 2 天同条，正常重处理 / 阿塞拜疆语 AYKA 14 Temu 七层木质鞋架 VFLkGOCO-RA / 德语 Sturmwaffel 厨房小工具吐槽 EE5YZq0-ZAE / 英语 Katie Roams Temu 迷彩帐篷野外过夜 TnvXELThO4w——冷凝水严重判不推荐，字幕为阿语自动译文 / 阿尔巴尼亚语 Temu 假牙饰挑战 Jxly_HLNsag）；1 个无字幕仅翻译（英语 Dope As Yola "Testing 420 Products"，年龄限制降级，420=大麻周边专区 -W7c4JkSA7k）；1 个剔除（naWuGbACsss 西语 Roblox "Dannita de Temu" 山寨梗词短剧，同 10-06 的 XpjArY648PI 类）。
- **本次翻车与自救（重要教训）**：首版临时 AI 脚本漏写 `new_videos.append(v)`（非 exclude 分支只改不存），inbox JSON 被写成只剩 1 条 exclude，且首跑 update_youtube.py 报「61 在页/新增 0」被误读为正常。识别方法：merge 输出「新增/更新 0」+页面缺今日 videoId+grep videoId 计数对不上=上游 JSON 残缺导致循环静默跳过。自救：重跑 fetch（同 8 条）→ 修正脚本重放 → 合并 68 在页。**今后写回类临时脚本必须 assert 条目数不变。**
- rebase 第 13 天连冲突，abort 重试仍冲突。沿用重建方案：backup/main-20261008 → reset --hard 到远端 be15d0f（Actions 10-07 19:19 UTC）→ 重跑 update_youtube.py（68 视频在页）。
- 提交 3eb0b18 推送成功。最终核验：68 视频、52 个 summarySource=ai 全带 aiSummary、今日 7 条全部在页且来源正确、19 条历史噪声零混入、昨日 8 条逐条 diff 无降级（X43Erz10Do8 今日重处理刷新文本属预期）。6 条 fetchedAt≤09-27 的旧视频按 10 天保留窗口自然过期出页。
- 临时脚本与临时文件已删除；scripts/ 与 .env.local 未动。备份分支 backup/main-20261008 保留。

## 2026-10-07 08:30
- 抓取成功：96 候选 → 8 视频（6 带字幕、2 降级描述），inbox/youtube-2026-10-07.json。
- AI 处理：4 个 AI 总结+标题热评翻译（阿塞拜疆语 AYKA 14 居家 vlog——Temu 手机壳 3-5 马纳特实测 X43Erz10Do8 / 英语情感故事"31 美元 Temu 求婚戒指"JpBa6dABzAI——评论区指出疑似 AI 生成剧情，如实注明 / 乌克兰语 ELENA_KISS 上学好物开箱 d5Awt1IdSnw——连续第 2 天同条，英语自动译文 / 俄语 OSIA 居家 vlog 罗马单身派对+新家具+Temu 足球袜 J4UTyNY4U3o）；2 个无字幕仅翻译（英语 ASMR Lisandra 捏捏乐打分 1pRaG1rIUbw / 塞尔维亚语 Milica&Barbara Temu 购物分享 R2ImfKqrJx4）；2 个剔除（J7N6du3HdJQ 摩洛哥宗教说教 #temu 纯引流 / UJ3lrHn0BqQ 波语 "2,5 roku temu" 词形巧合的金属探测器寻宝视频）。
- rebase 第 12 天连冲突，abort 重试仍冲突。沿用重建方案：backup/main-20261007 → reset --hard 到远端 22899d0（Actions 10-06 18:53 UTC）→ 重跑 update_youtube.py（68 视频在页）。
- **第 7 次抓到 Actions 带回历史噪声**：XpjArY648PI（西语 Roblox 假冒诈骗短剧）被远端基底带回，再次以 exclude 条目剔除，最终 67 视频在页。昨日 7 条 AI 视频本次完好无降级。
- 提交 7c4a0da 推送成功。最终核验：67 视频、51 个 summarySource=ai 全带 aiSummary、标记零不一致、噪声零混入。
- 临时脚本与临时文件已删除；scripts/ 与 .env.local 未动。备份分支 backup/main-20261007 保留。

## 2026-10-06 08:30
- 抓取成功：94 候选 → 8 视频（7 带字幕、1 降级描述），inbox/youtube-2026-10-06.json。
- AI 处理：4 个 AI 总结+标题热评翻译（德语 Torben Platzer 实测 Temu AI 小玩意——1033 欧 9 件含 3D 打印机/机器狗，结论"蹭 AI 的含金量极低"，字幕为英语 NszDvQEHQ5w / 英语家庭 Temu 购物翻车搞笑短视频 1-6617ujgcs（阿语自动译文，如实注明娱乐短剧）/ 乌克兰语 ELENA_KISS"上学好物"开箱 d5Awt1IdSnw（英语自动译文，博主提及因战乱无法回国过万圣节）/ 波语 Muffinaart 实测贵价商品 S545-gfOBIs——Temu 波兰本地仓三天到货）；1 个无字幕仅翻译（克罗地亚语 ArtDaNova 秋季开箱 ftHT4Qeh5vg，描述带 100 欧优惠券码 kfp3647 属联盟带货）；3 个剔除（XpjArY648PI 西语"我频道的 Temu 版本"=山寨梗词实为 Roblox 假冒诈骗短剧 / 7h6KFkysZyw 阿语摩洛哥荒诞伦理故事 #temu 引流 / 95zxcL-_3GU 波语 "POMOGŁEM TEMU FACETOWI" 中 temu 为指示代词词形巧合）。
- rebase 第 11 天连冲突，abort 重试仍冲突。沿用重建方案：backup/main-20261006 → reset --hard 到远端 2f44b34（Actions 10-05 21:05 UTC）→ 重跑 update_youtube.py（65 视频在页，远端基底比本地多 1 条）→ 单次提交 adda339 推送成功。
- 最终核验通过：65 视频、52 个 summarySource=ai 全带 aiSummary、昨日/前日 12 条 AI 视频全部完好无降级、17 条历史噪声零混入。
- 临时脚本已删除；scripts/ 与 .env.local 未动。备份分支 backup/main-20261006 保留。

## 2026-10-04 08:30
- 抓取成功：8 视频（7 带字幕、1 降级描述），inbox/youtube-2026-10-04.json。
- AI 处理：7 个 AI 总结+标题热评翻译（印地转写英语"amir from temu"配送员搞笑短剧 VIp4XYMw0nE，与昨日同条正常重处理 / 法语 Tibo 俯卧撑板差评 2/10 k7KHVevAz-w / 英语 1星vs5星商品对比 Wk_0qmhes7I（transcript 为阿语自动译文）/ 乌克兰语 20 件厨房用品 goFKBEVnMXE（昨日同条）/ 英语 $1000 充气帐篷生存挑战 0Kntn7OYT8Y（阿语自动译文）/ 法语 Tibo 俯卧撑支架好评 7/10 1JrjDnZWCg8 / 西语优惠码带货开箱 qGKVHlXHpBY，如实注明为联盟带货非中立测评）；1 个无字幕仅翻译（日语生ジェラート吃播 5YbePSTahbM）；0 个剔除（今日 8 条均为 Temu 相关）。
- rebase 第 9 天连冲突，abort 重试（即首次尝试）仍冲突。沿用重建方案：backup/main-20261004 → reset --hard 到远端 f495f1a → 重跑 update_youtube.py（61 视频在页）→ 单次提交 3ab5c8e 推送成功。
- **第 5 次抓到 Actions 降级**：昨日 AI 视频 vfDOv2zCL-s（Temu 改装福特嘉年华收官集）被云端 Actions 17:11 UTC 那轮降回 description。已从 backup/main-20261003 取回整条恢复；同时昨日已剔除的噪声 5onNmbtq5Uo（阿语突尼斯少女故事 #temu 引流）又被云端抓回，已再次移除。
- **脚本教训**：json.JSONDecoder().raw_decode(html[i:]) 返回的 end 是子串内偏移，取 JSON 必须用 html[i:i+end] 而非 html[i:end]（后者在 end<i 时得到空串导致 JSONDecodeError）。首版修复脚本因此报错，未写坏文件，改正后通过。
- 最终核验通过：60 视频、47 个 summarySource=ai 全带 aiSummary、标记零不一致、噪声零混入。
- 临时脚本已删除；scripts/ 与 .env.local 未动。备份分支 backup/main-20261004 保留。

## 2026-10-03 08:30
- 抓取成功：8 视频全带字幕，inbox/youtube-2026-10-03.json。
- AI 处理：7 个 AI 总结+标题热评翻译（英语 "amir from temu" 印度外卖员搞笑短剧 VIp4XYMw0nE——Temu 为梗设但整体围绕 Temu 配送员，保留并如实注明是娱乐短剧 / 阿塞拜疆语 400 马纳特包裹 3ZmoMQUUQRs / 英语 $200 压缩沙发三天回访 GW7ktkQAt3o / 英语 Temu 改装福特嘉年华收官集 vfDOv2zCL-s / 波兰语数码小件实测+关税讲解 pVibmRyTXc4 / 英语 Badbishlily 最怪商品开箱 3mROJj4VBUA / 乌克兰语 20 件厨房用品"厨房还是垃圾桶" goFKBEVnMXE）；1 个剔除（5onNmbtq5Uo 阿语突尼斯少女案件故事，#temu 纯引流标签）。
- rebase 第 8 天连冲突，abort 重试仍冲突。沿用重建方案：backup/main-20261003 → reset --hard 到远端 5924db0 → 重跑 update_youtube.py → 单次提交 c31840b 推送成功。
- **又抓到 Actions 降级**：昨日 AI 视频 i0JtDOaeoLI（Temu 思域赛道实测）被 Actions 凌晨刷新降回 transcript——云端 Actions 在本地 fix（96dbc96）之后又跑了一轮。已从备份分支取回整条补回；同时 neJAWdLViAk（COD 皮肤梗）又被云端抓回，已再次移除。fix 提交 6ca75ac 推送成功。
- **核验脚本教训**：minified 单行 YOUTUBE_DATA 后面紧跟 `;/* <<<YOUTUBE_DATA_END>>> */`，正则 `\{.*?\});\s*\n` 会在 JSON 真实结尾匹配不上（`}` 后是 `;` 再是 `/` 不是换行），越过 JSON 一直吞到页面后面第一个 `});\n`，导致 json.loads "Extra data" 假报错。核验应改用 json.JSONDecoder().raw_decode（从 "const YOUTUBE_DATA = " 之后解析，raw_decode 返回真实结束位置）。文件本身无损，diff 里 5002 行删除只是 pretty→minified。
- 最终核验通过：72 视频、46 个 summarySource=ai 全带 aiSummary、标记零不一致、三个历史噪声（5onNmbtq5Uo/EbP/neJAWdLViAk）均不在页。
- 临时脚本已删除；scripts/ 与 .env.local 未动。备份分支 backup/main-20261003 保留。

## 2026-10-02 08:30
- 抓取成功：8 视频（7 带字幕、1 降级描述），inbox/youtube-2026-10-02.json。
- AI 处理：6 个 AI 总结+标题热评翻译（英语 Temu 思域赛道实测 i0JtDOaeoLI——transcript 是孟加拉语自动译文但内容完整 / 韩语主播 Temu 广告开箱 2bAfrvVoh0I / 阿语 Temu 和面机整蛊妈妈 uSLG7dhAmJA（连续第 3 天被抓回，正常重处理）/ 阿塞拜疆语 400 马纳特包裹 3ZmoMQUUQRs / 波兰语爆款实测 4RApBIZcMvc / 西语摩托尾箱包对比 Amazon D9GyGgtcMRI）；1 个无字幕仅翻译（日语巧克力 ASMR woH8ikyrdvo，连续第 3 天）；1 个剔除（neJAWdLViAk COD Mobile"Temu Ghost"皮肤视频，Temu 纯梗词，同昨日"TEMU GTA 6"性质）。
- rebase 第 7 天连冲突，abort 重试仍冲突。沿用重建方案：backup/main-20261002 → reset --hard 到远端 f303109 → 重跑 update_youtube.py → 单次提交 92075b8 推送成功。
- 核验通过：71 视频、36 个 summarySource=ai 全带 aiSummary、标记零不一致（今日新增 6 个；历史重点 VUZEfG0ebbE / 127AeMh2DFY / PdLEnJlxLEA 完整，EbP 与 neJAWdLViAk 均不在页）。
- 核验脚本注意：YOUTUBE_DATA 是 `const YOUTUBE_DATA = {...}` 对象（含 videos 字段），不是裸数组，正则要按对象解析。
- 临时脚本已删除；scripts/ 与 .env.local 未动。备份分支 backup/main-20261002 保留。

## 2026-10-01 08:30
- 抓取成功：8 视频（6 带字幕、2 降级描述），inbox/youtube-2026-10-01.json。
- AI 处理：5 个 AI 总结+标题热评翻译（罗马尼亚语摩托护具实测重抓 127AeMh2DFY / 西语 Temu 网红空调开箱 PdLEnJlxLEA / 韩语主播 Temu 广告开箱 2bAfrvVoh0I / 阿语 Temu 和面机整蛊妈妈 uSLG7dhAmJA / 波兰语 Temu 爆款实测 4RApBIZcMvc）；2 个无字幕仅翻译（Tibo 法语健身器材快评 QbPSlaOOdN8 / 日语巧克力 ASMR woH8ikyrdvo）；1 个剔除（EbP-k9kfqBE 印尼语 "temu kangen"=重逢闲聊，昨日已剔，今日又被抓回）。
- rebase 第 6 天连冲突，abort 重试仍冲突。沿用重建方案：backup/main-20261001 → reset --hard 到远端 668d0b9 → 重跑 update_youtube.py → 单次提交 fd85f71 推送成功。
- **第 3 次抓到 Actions 降级**：远端基底把 VUZEfG0ebbE（Temu 食材做菜）从 ai 降回 description、中文标题和 aiSummary 全丢。已从备份分支取回整条补回，fix 提交 58d25ef 推送成功。
- 核验通过：69 视频、32 个 summarySource=ai 全带 aiSummary、标记零不一致、EbP 已不在页。
- 临时脚本已删除；scripts/ 与 .env.local 未动。备份分支 backup/main-20261001 保留。
- 注意：rebase 前必须先 commit（工作区有未暂存 index.html 会直接拒绝 rebase），本次又验证了一遍。

## 2026-09-30 08:30
- 抓取成功：8 视频全带字幕，inbox/youtube-2026-09-30.json。
- AI 处理：5 个 AI 总结+标题热评翻译（孟加拉语 $1800 越野摩托开箱 XZYcGyG0W5c / 英语 Tibo 倒挂靴+弓形按摩棒 rMzBiMlb72A / 罗马尼亚语摩托护具实测 127AeMh2DFY / 西语捏捏乐带货 2TDl3AbBhoQ / 捷克语一星差评商品实测 5t__8fYvw5I）；3 个剔除（CQmcyB9p31c 西语 "El Payaso de Temu"=山寨梗词实为麦当劳小丑故事、EbP-k9kfqBE 印尼语 "temu kangen"=重逢闲聊、wU1-6bneE1k 摩洛哥出租车故事 #temu 引流）。
- rebase 第 5 天连冲突，abort 重试仍冲突。沿用重建方案：backup/main-20260930 → reset --hard 到远端 6036bb6 → 重跑 update_youtube.py → 单次提交 b2a986a 推送成功。
- **再次抓到 Actions 降级**：远端基底丢失昨日 AI 视频 4rVBHMnsHgQ（德国 0 欧捏捏乐），已从备份分支取回补回，fix 提交 94b94df 推送成功。本次补回时顺带把 YOUTUBE_DATA 压缩为单行 minified（内容不变，页面少 3800 行）。
- 核验通过：59 视频、27 个 summarySource=ai 全带 aiSummary、标记零不一致（今日新增 5 个，历史 22 个完整）。
- 临时脚本已删除；scripts/ 与 .env.local 未动。备份分支 backup/main-20260930 保留。

## 2026-09-29 08:30
- 抓取成功：99 候选 → 8 视频全带字幕，inbox/youtube-2026-09-29.json。
- AI 处理：7 个 AI 总结+标题热评翻译（法语 Tibo 健身小件快评 0fPjzG-fsyQ / 英语 1星vs5星实测 CGQ1uHMl96Q / 英语 Temu 充气帐篷风暴实测 g5tRqPQ0Or0 / 德语 0 元捏捏乐带货 4rVBHMnsHgQ / 孟加拉语 $1800 越野摩托开箱 XZYcGyG0W5c / 法语 Tibo 呼啦圈+杠铃护角 BiToIuubmes / 英语 Tibo 倒挂靴+弓形按摩棒 rMzBiMlb72A）；1 个剔除（CQmcyB9p31c 西语 "El Payaso de Temu"——"Temu 小丑"=廉价山寨梗词，实为麦克唐纳小丑恐怖故事）。
- rebase 第 4 天连冲突，abort 重试仍冲突。沿用重建方案：backup/main-20260929 → reset --hard 到远端 5ee8e0a → 重跑 update_youtube.py → 单次提交 e2ac3a1 推送成功。
- 核验通过：56 视频、24 个 summarySource=ai 全带 aiSummary、标记零不一致（今日新增 7 个，历史 17 个无丢失）。
- 临时脚本已删除；scripts/ 与 .env.local 未动。备份分支 backup/main-20260929 保留。

## 2026-09-28 08:30
- 抓取成功：94 候选 → 8 视频全带字幕，inbox/youtube-2026-09-28.json。
- AI 处理：7 个 AI 总结+标题热评翻译（法语 Tibo 健身小件快评 0fPjzG-fsyQ / 英语 1星vs5星实测 CGQ1uHMl96Q / 英语 $200 压缩沙发 BqKAb8H9Syc / 英语 Temu 充气帐篷风暴实测 g5tRqPQ0Or0 / 法语 Tibo 呼啦圈+护角 BiToIuubmes / 僧伽罗语时隔一年开箱 rEEGeojYdjU / 阿塞拜疆语开箱 TC5vk83ehS4）；1 个剔除（Vz22V6HLy6o 印尼语古装剧解说，temu=印尼语"找到"，非平台）。
- rebase 第 3 天连冲突（本地 fe45e79 vs 远端 9708139），abort 重试仍冲突。沿用重建方案：backup/main-20260928 → reset --hard 到远端 → 重跑 update_youtube.py（51 视频在页）→ 单次提交 1032403 推送成功。
- 核验通过：解析 YOUTUBE_DATA，51 视频、21 个 summarySource=ai 全带 aiSummary、标记零不一致（今日新增 7 个）。
- 临时脚本已删除；scripts/ 与 .env.local 未动。备份分支 backup/main-20260928 保留。

## 2026-09-27 08:30
- 抓取成功：8 视频全带字幕，inbox/youtube-2026-09-27.json。
- AI 处理：5 个 AI 总结+标题热评翻译（英语猎奇数码测评 yQIiuhYTD6c / 僧伽罗语手机壳开箱 rEEGeojYdjU / 孟加拉语捏捏乐带货 AbqubLeXVuo / 西语 Temu 假 iPhone 翻车 Rm1Kl9-v8Pc / 意语 100 欧爆款开箱 Q0v1sM3WmjM）；3 个剔除（DbZrtKbb1ro "Temu Supercar"=劣质车调侃昵称实为超跑维修、zJoks4O0G1I 波语 GTA6 典藏版与 09-26 同条、RwN8VbmEE88 阿语伦理故事 #temu 引流）。
- **rebase 又冲突**（本地 21e44d7 vs 远端 Actions 566565b），abort 重试一次仍冲突。直接沿用重建方案：backup/main-20260927 → reset --hard 到远端 → 重跑 update_youtube.py（41 视频在页）→ 单次提交 cfccbb9 推送成功。
- **核验发现 2 个历史 AI 视频被 Actions 降级**：E9iiFEykA3M（£1000 开箱）、yzBXRezNa7w（泳池神器）aiSummary 和中文标题完好但 summarySource 变回 transcript——再次证实 Actions 保护逻辑不可靠。已在本次提交中把标记修回 ai。今后每次重建基底后都要解析 YOUTUBE_DATA 逐条核对 summarySource 与 aiSummary 一致性（不能只数 aiSummary 数量）。
- 最终：页面 41 视频、14 个 aiSummary（source 标记全部一致）。临时脚本均已删除；scripts/ 与 .env.local 未动。备份分支 backup/main-20260927 保留。

## 2026-09-26 08:30
- 抓取成功：8 视频（7 带字幕），inbox/youtube-2026-09-26.json。
- AI 处理：3 个 AI 总结+标题热评翻译（俄语 BANARU 装修开箱+搭菜畦 sx3CGofrc4A / 希伯来语泳池用品测评 ywE8595N0F8 / 西语 Temu 拟人讽刺短剧 vr3GDuL1dj4）；1 个无字幕仅翻译（英语 ASMR 捏捏乐 sh_F8m6Oj6E）；4 个剔除（XEOORQGckI4 "Temu Zack D. Films"=山寨梗词、UxI_qslTiEY 阿语励志故事纯 #temu 引流、zJoks4O0G1I 波语 GTA6 典藏版 "z TEMU"=劣质代名词、CdW4Jn3KJg4 波语 "temu chłopcu"=指示代词巧合）。
- **push 又遇 rebase 死结**（同昨日）：本地提交与远端 Actions 在 index.html 冲突，abort 重试一次无效。直接沿用昨日验证过的重建方案：备份分支 backup/main-20260926 → reset --hard 到远端 673d50b → 重跑 update_youtube.py（inbox 被 gitignore，数据无损）→ 单次提交 889db7d 推送成功。注意：git add/commit 要放在 pull --rebase 之前（工作区有未暂存的 index.html 会导致 rebase 直接拒绝）。
- **发现并修复云端 Actions 的保护漏洞**：远端基底上昨日 AI 视频 lu5f9dJJnhs（捏捏乐带货 kou4989）被 Actions 夜间刷新降级回 description、aiSummary 丢失——说明 Actions 保护逻辑并非完全可靠。已从昨日 inbox 文件取回 AI 文本补回页面，提交 86e6e25 推送成功。今后重建基底后应核对上一日 AI 视频是否完整。
- 最终：页面 33 视频、11 个 aiSummary（逐视频核验通过）。临时脚本均已删除；scripts/ 与 .env.local 未动。

## 2026-09-25 08:30
- 抓取成功：96 候选 → 8 视频全带字幕，inbox/youtube-2026-09-25.json。
- AI 处理：6 个 AI 总结+标题热评翻译（捏捏乐带货 kou4989 / 西语假金条翻车 / 阿塞拜疆秋季服装开箱 / 泰卢固语 0 元购推广 / 俄语 Temu 开箱+施工 / 希伯来语泳池用品测评）；2 个剔除（U59LwDHDB-E 律师反应视频、5hKSjl39voM "TEMU GTA 6"——Temu 仅作梗词，内容与平台无关）。
- **解决历史 rebase 死结**：昨日遗留 3 个未推送本地提交（7f5c0cc/96a049b/4ab6ec1）与远端 Actions 在 index.html 确定性冲突，盲目 abort 重试无解。改用重建方案：建备份分支 backup/main-20260925 + 备份 inbox 到 /tmp → reset --hard 到远端 502d81b → 依次重跑 update_youtube.py（09-24 文件、09-25 文件、80rkfUrOVMc 剔除补丁）→ 一次提交 74c89ef 推送成功。inbox 未被 git 跟踪（.gitignore），reset 不影响数据源。
- 经验：update_youtube.py 处理 exclude 条目是直接从页面删除视频（不是写 exclude 标记）；云端 Actions 的保护逻辑只保留页面里已有的 aiSummary，所以拿远端做基底重跑 inbox 合并可无损恢复 AI 总结。
- 最终：页面 27 视频、10 处 aiSummary（4 历史+6 今日）。备份分支 backup/main-20260925 保留，确认无虞后可删。

## 2026-09-24 08:30
- 抓取成功：95 候选 → 8 视频，inbox/youtube-2026-09-24.json（6 个带字幕）。
- AI 处理：6 个 AI 总结（写入 aiSummary、summarySource=ai、标题+热评翻译）；2 个剔除（7cfI_KyhOBg 阿语家庭伦理故事 #temu 引流、80rkfUrOVMc 波语 "temu"=之前的词形巧合）。
- 合并成功：update_youtube.py 报 21 视频在页。
- **push 失败**：git pull --rebase 与远端 900a152（Actions "chore: 刷新数据 2026-09-23 17:50 UTC"）在 index.html 冲突，abort 重试一次仍冲突，按预案放弃 push。本地提交 7f5c0cc 未推送，留在 main 上，下次运行 rebase 前需先解决。
- 备注：临时脚本已删除；scripts/ 与 .env.local 未动。

## 2026-10-05 08:30
- 抓取成功：97 候选 → 8 视频（7 带字幕、1 降级描述），inbox/youtube-2026-10-05.json。详情拉取时代理 503 一次但重试后正常。
- AI 处理：7 个 AI 总结+标题热评翻译（英语 Gary Martin 实测 Temu 三支 60 度挖起杆——PXG 仿款最好 Titleist 仿款最弱 s9PO608eDpQ，字幕为阿语自动译文 / 俄语 ZARA+COS 等购物分享（Temu 仅红色泳衣一件单品，如实注明）eaaoWadQibk / 英语 JazzTech USB 检测仪汇总评测 z7clh1L4V3w（阿语自动译文）/ 阿语捏捏乐开箱 RI3VOj98nPU（brieffnews 联盟带货账号、标题带优惠码 ALR741870，如实注明）/ 英语 Clare Walch 十月大采购含沙发评测 R9naMlDSQ0Q / 英语 Temu 宣传小剧+防钓鱼科普 V-MZjGINhD8（如实注明是宣传短剧）/ 英语 Dean Harding £127 Yamahero P790 仿款铁杆开箱 _MzdoBZ7Xqw）；1 个无字幕仅翻译（乌尔都语低质 haul 短视频 gyhP6YoDGrk，标题是求订阅引流但内容确为 Temu 服装开箱，保留）；0 个剔除（今日 8 条均与 Temu 相关）。
- rebase 第 10 天连冲突，abort 重试仍冲突。沿用重建方案：backup/main-20261005 → reset --hard 到远端 96d04fe → 重跑 update_youtube.py → 单次提交 13a0d8b 推送成功。
- **第 6 次抓到 Actions 降级，且一次降了 5 条**：昨日 AI 视频 Wk_0qmhes7I / 0Kntn7OYT8Y / qGKVHlXHpBY / TI-Np0150no 被云端 Actions 17:25 UTC 那轮降回 description（TI-Np0150no 首轮核验清单漏查、二次全量比对才发现——核验必须拿昨日 inbox 全部条目逐条 diff，不能只查抽查清单）。已从 inbox/youtube-2026-10-04.json 取回整条恢复；同时历史噪声 UxI_qslTiEY（阿语励志故事引流）和 DbZrtKbb1ro（超跑维修）被远端基底带回，已再次剔除。fix 提交 1f42f24 推送成功。
- 最终核验通过：68 视频、54 个 summarySource=ai 全带 aiSummary、标记零不一致、昨日 8 条逐字段 diff 全一致、12 条历史噪声零混入。
- 临时脚本与临时文件已删除；scripts/ 与 .env.local 未动。备份分支 backup/main-20261005 保留。

## 2026-10-10 08:30
- 抓取成功：98 候选 → 8 视频全带字幕，inbox/youtube-2026-10-10.json。
- AI 处理：6 个 AI 总结+标题热评翻译（德语 Sturmwaffel 切面包板 3/5 分、刀卡塑料槽 13.81 欧 DJUcmfE4qrs / 日语 USB 优盘 20 支批量购 #PR 植入 vv6dyLyTUiA——连续第 2 天同条 / 法语 Tibo InShape Temu 走步机约 150 欧 9/10 高分 cRxxajisgL4 / 阿塞拜疆语 AYKA 14 回应恶评 vlog，标题称 Temu 买机器人但购物占比小 ZSAZCjdq5l0 / 德语 Sturmwaffel 芒果取肉器 8.28 欧判多余 GUFuzSDn9TQ / 英语游戏收藏博主 Temu 买 Switch 港版疑翻新机，字幕为孟加拉语自动译文 FoWeKBwtNzE）；0 个无字幕；2 个剔除（Ii9LrghHMSM 印尼语时政直播 temu=会面，连续第 2 天 / S6eD8KhE89w "TEMU MK" 街球 1v1，Temu 为山寨梗词）。
- rebase 第 15 天连冲突，abort 重试仍冲突。沿用重建方案：backup/main-20261010 → reset --hard 到远端 d7f4bed（Actions 10-09 18:46 UTC）→ 重跑 update_youtube.py（68 在页，远端基底多 1 条）。
- **第 8 次抓到 Actions 带回历史噪声**：LROBGBZXj5s（"TEMU SOLO LEVELING" 山寨梗词，昨日刚剔）被远端基底带回，已打剔除补丁移除，最终 67 视频在页。
- 提交 2df238a 推送成功。最终核验：67 视频、49 个 summarySource=ai 全带 aiSummary、今日 6 条全在页、昨日 5 条 AI 视频无降级、10 条重点噪声零混入。
- 临时脚本已删除（写回脚本含条目数与 videoId 集合 assert）；scripts/ 与 .env.local 未动。备份分支 backup/main-20261010 保留。

## 2026-10-14 08:30
- 抓取成功：97 候选 → 8 视频全带字幕，inbox/youtube-2026-10-14.json。
- AI 处理：6 个 AI 总结+标题热评翻译（英语 More WillNE 团队实测 Temu 奢侈品（梵克雅宝风格手链做工精致/金扑克噱头/6 英尺狮子像）GgoSemqgyns——连续第 3 天同条 / 德语 Mohi Toys Amazon vs Temu 玩具对比本集 Temu 全胜 CPFa2_oa-Ls——连续第 3 天 / 英语 Chris Slix 自述 Temu 买宾利车身套件翻车、尾部尺寸不对交 Chrome&Carbon 返工，累计花 10 万英镑 IzsGMxNIdac / 英语 Joe Bart 4.5 小时直播回放（26:08-1:46 为 Temu 推荐页挑选环节）xsIyvLk_ZAE / 捷克语 Vítek 零基础实测 Temu 最便宜渔具 3000 克朗钓上第一条鱼 _5STtQUHvC8 / 英语 Joe Bart 剪辑：观众投票买猎奇商品 faF5S0e5NGQ）；0 个无字幕；2 个剔除（lik2iCqzVjs 阿语摩洛哥婚姻伦理故事 #temu 纯引流 / yVq9ppQeGD8 "Zack D Films From Temu" 山寨梗词，同 09-26 XEOORQGckI4 先例）。
- rebase 第 18 天连冲突，abort 重试仍冲突。沿用重建方案：backup/main-20261014 → reset --hard 到远端 c025451（Actions 10-13 19:52 UTC）→ 重跑 update_youtube.py（69 在页）。
- **第 11 次抓到 Actions 带回历史噪声**：A7yGA-VTRbI（3.7 小时日语闲聊直播）再次被远端基底带回，剔除补丁后 68 在页。
- 提交 731fab4 推送成功。最终核验：68 视频、50 个 summarySource=ai 全带 aiSummary、今日 6 条全在页、20 条重点噪声零混入（A7yGA-VTRbI 已剔）。核对清单笔误提醒：昨日 Mohi Toys 正确 ID 是 CPFa2_oa-Ls、Noraafitt 视频是 x_AT0ctikNI（kev5423 是优惠码不是 videoId）。
- 临时脚本与临时补丁已删除（写回脚本含条目数/顺序/统计 assert）；scripts/ 与 .env.local 未动。备份分支 backup/main-20261014 保留。
