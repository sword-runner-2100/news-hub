# Automation 9dfd1aaa 执行记录（每日 YouTube Temu 抓取 + AI 总结）

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
