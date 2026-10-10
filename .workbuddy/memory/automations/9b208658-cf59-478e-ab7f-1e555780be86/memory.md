# YouTube Temu 视频抓取自动化 — 执行记录

## 2026-09-23 20:30
- 状态：成功（[OK]，无 SKIP/FAIL）
- 抓取：8 个视频，全部带字幕（summarySource=transcript）
- AI 总结：6 个（写入 aiSummary + summarySource 改为 "ai"，title/热评已翻译中文）
- 剔除噪声：2 个 → {"videoId":"...","exclude":true}
  - 7cfI_KyhOBg：阿拉伯语家庭故事，temu 仅出现在标签
  - 1sAJ5oAol8k：塞尔维亚真人秀，"temu" 为斯拉夫语"话题"词义巧合
- 合并：update_youtube.py 成功，页面共 19 个视频（新增/更新 7）
- 推送：首次 git pull --rebase 因工作区有未提交改动失败；调整顺序（先 commit 再 pull --rebase 再 push）后成功，commit 9acb4e9
- 经验：rebase 前若工作区有改动，先 commit 本地改动再 rebase

## 2026-09-24 20:30
- 状态：抓取成功（[OK]），但 **push 失败**
- 抓取：8 个视频，全部带字幕
- AI 总结：5 个（x3Btp0JsXJM 翻车合集、_xmQWD8CD98 翻车合集P1、PNfl-QetgSc 阿塞拜疆秋装Vlog、zSvxm8s86BE 西语假金条、lu5f9dJJnhs 捏捏乐带货）
- 剔除噪声：3 个 → exclude:true
  - 7cfI_KyhOBg：阿拉伯语家庭故事（与昨日同视频），temu 仅在标签
  - uYCYriR5nQk：阿尔巴尼亚语纯引流码推广
  - U59LwDHDB-E：律师反应视频，"Temu" 仅是标题玩梗（山寨版 Zack D Films），内容与 Temu 购物无关
- 合并：update_youtube.py 成功，页面共 22 个视频（新增/更新 6）
- push：本地先 commit（96a049b）后 pull --rebase，回放今晨旧 commit 7f5c0cc（08:36 的 YouTube 刷新）时与云端 900a152..213567f 冲突；abort 重试一次仍同冲突 → 按预案放弃 push
- 遗留：本地 main 领先远端 2 个 commit（7f5c0cc、96a049b），未推送；云端 21:00 的 GitHub Actions 9 点档可能跑在云端，其有保护逻辑不会覆盖，但本地 AI 总结需用户手动解决冲突后 push（建议下次执行前先处理 rebase 冲突或 drop 旧 commit）
- 经验：早晨那次任务如果 push 失败遗留本地 commit，晚上 rebase 时会被再次回放导致冲突；冲突根源是 7f5c0cc 而非本次 96a049b

## 2026-09-25 20:30
- 状态：成功（[OK]，push 成功 c9c466e）
- 抓取：8 个视频，全部带字幕
- AI 总结：5 个（zSvxm8s86BE 西语假金条加热露馅、lu5f9dJJnhs 捏捏乐推广码带货、sx3CGofrc4A 俄语装修+Temu 开箱、ywE8595N0F8 希伯来语泳池用品测评、lNDPkUkmktg 意语加拉斯科案评论+Temu 赞助段，已如实注明主体非 Temu）
- 剔除噪声：3 个 → exclude:true
  - U59LwDHDB-E：律师反应视频（连续第三天出现），Temu 仅标题玩梗
  - 5hKSjl39voM："TEMU GTA 6"AI 恶搞短剧，Temu 为"山寨"俚语，与 Temu 购物无关
  - XEOORQGckI4：阿拉伯语"Temu Zack D Films"反应视频，同上玩梗
- 合并：update_youtube.py 首次跑 28 个视频
- push：pull --rebase 与远端新 commit 847afc1（Actions 新闻数据刷新 06:03 UTC）在 index.html 冲突；abort 重试一次仍冲突 → 改用机械解法成功：checkout --ours（远端为底）+ 重跑 update_youtube.py 重放 YouTube 数据 + rebase --continue，两侧数据都保留，最终页面 29 个视频
- 经验：与 Actions 数据刷新冲突时，"远端为底+重跑 update 脚本"比手工解冲突标记更稳，优于放弃 push

## 2026-09-26 20:30
- 状态：成功（[OK]，push 成功，最终 commit f22cfb1）
- 抓取：8 个视频，7 个带字幕（sh_F8m6Oj6E 捏捏乐视频 TranscriptsDisabled 降级为描述摘录）
- AI 总结：5 个（sx3CGofrc4A 俄语装修+Temu开箱已注明施工为主线、vr3GDuL1dj4 西语"如果Temu是一个人"讽刺拉新套路小品、DbZrtKbb1ro Temu超跑故障诊断、yQIiuhYTD6c 怪异Temu科技、mD9x-97tY8Q Fiat 500 Temu改装）；1 个无字幕仅翻译（sh_F8m6Oj6E）
- 剔除噪声：2 个 → exclude:true
  - XEOORQGckI4：阿拉伯语"Try Not To Laugh At Temu Zack D. Films"反应视频，Temu 仅标题玩梗
  - zJoks4O0G1I：波兰语 GTA6 典藏版评测（1800兹罗提不含游戏），"TEMU"是"山寨廉价"俚语
- 合并：update_youtube.py 首次 36 个视频，冲突重放后 37 个
- push：pull --rebase 与远端 7db8a1d（Actions 06:02 UTC 刷新）冲突，abort 重试一次仍冲突 → 机械解法成功（checkout --ours 远端为底 + rebase --continue + 重跑 update_youtube.py 重放），页面共 37 个视频，AI 总结验证完好（页面 summarySource=ai 共 11 条）
- 机械解法第二次成功验证，已作为标准流程

## 2026-09-27 20:30
- 状态：成功（[OK]，push 成功，最终 commit e10f65b）
- 抓取：8 个视频，全部带字幕
- AI 总结：6 个（DbZrtKbb1ro Temu超跑故障排查-连续第二天上榜、yQIiuhYTD6c 怪异Temu科技-连续第二天、rEEGeojYdjU 斯里兰卡语一年后再开箱、AbqubLeXVuo 孟加拉语捏捏乐推广码带货、TC5vk83ehS4 阿塞拜疆语订单开箱、1ko2bqQozLA 4小时直播Temu生存装备实测）
- 剔除噪声：2 个 → exclude:true
  - RwN8VbmEE88：阿拉伯语/摩洛哥方言道德故事，temu 仅在标签
  - YLqImiloSv0：MMA 柔术黑带故事短视频，"Temu" 是"地摊货/假货"俚语玩梗
- 合并：update_youtube.py 首次 44 个视频，冲突重放后 46 个
- push：pull --rebase 与远端 9f6963b（Actions 刷新）冲突 → 机械解法一次成功（checkout --ours 远端为底 + rebase --continue + 重跑 update_youtube.py 重放），页面 46 个视频，AI 总结验证完好（summarySource=ai 共 17 条）
- 机械解法第三次成功验证，标准流程稳定

## 2026-09-28 20:30
- 状态：成功（[OK]，push 成功，最终 commit 70a688a）
- 抓取：8 个视频，仅 2 个拿到字幕（当天 YouTube 直连+Invidious 大面积失败，6 个降级为描述摘录，其中含本应有字幕的英语视频）
- AI 总结：2 个（CGQ1uHMl96Q Drew 1星vs5星实测-结论一半惊喜一半翻车、ltZ05e1a60o simon42 德语智能家居坑货实测-300欧/投影仪疑连香港新加坡服务器）
- 仅翻译：4 个（0fPjzG-fsyQ 与 BiToIuubmes Tibo InShape 法语健身器材短视频、BqKAb8H9Syc 200美元沙发开箱、g5tRqPQ0Or0 充气帐篷露营）
- 剔除噪声：2 个 → exclude:true
  - CQmcyB9p31c：西语"Temu 小丑"恐怖短剧，Temu 为"山寨"俚语
  - Vz22V6HLy6o：印尼语家庭剧电影解说，"temu"是印尼语"遇见/得到"词义巧合
- 合并：update_youtube.py 首次 52 个视频，冲突重放后 53 个
- push：先 commit（f5a3903）再 pull --rebase，与远端 076fc8a（Actions 06:35 UTC 刷新）冲突，abort 重试一次仍冲突 → 机械解法第四次成功（checkout --ours 远端为底 + rebase --continue + 重跑 update_youtube.py 重放），页面 53 个视频，AI 总结验证完好（summarySource=ai 共 18 条）
- 踩坑：Write 工具会把中文文本里的弯引号「""」写成 ASCII 双引号导致 Python 脚本字符串断裂；临时脚本内嵌套引号一律用「」
- 注意：抓取耗时 10 分钟（字幕重试导致），远超平时 1 分钟，后台运行不影响结果

## 2026-09-29 20:30
- 状态：成功（[OK]，push 成功，最终 commit fcc27f3）
- 抓取：8 个视频，全部带字幕（耗时约 5 分钟）
- AI 总结：7 个（0fPjzG-fsyQ 与 rMzBiMlb72A 与 BiToIuubmes 均为 Tibo InShape 法语健身器材测评 Shorts——同一博主当天连发三条、内容不重复；CGQ1uHMl96Q Drew 一星vs五星-连续第二天（字幕被自动译成阿拉伯语）、g5tRqPQ0Or0 Matt Slays 充气帐篷-昨日无字幕今日补上总结（暴雨渗水+山火疏散）、4rVBHMnsHgQ 德语 0 欧捏捏乐兑换码带货（热评纠正小怪物=六角恐龙+童工批评）、XZYcGyG0W5c 孟加拉语 1800 美元 Temu 越野摩托组装）
- 剔除噪声：1 个 → exclude:true
  - CQmcyB9p31c：西语麦当劳小丑恐怖故事（连续第二天），Temu 仅标题玩梗
- 合并：update_youtube.py 首次 56 个视频，冲突重放后 56 个
- push：先 commit（b72b69c）再 pull --rebase，与远端 9c29f71（Actions 刷新）冲突，abort 重试一次仍冲突 → 机械解法第五次成功（checkout --ours 远端为底 + rebase --continue + 重跑 update_youtube.py 重放，重放显示新增/更新 8 个），页面 56 个视频，AI 总结验证完好（summarySource=ai 共 24 条 = 昨日 18 + 新增 6，CGQ1uHMl96Q 为沿用更新），噪声视频确认不在页面
- 机械解法已连续 5 次成功，标准流程稳定

## 2026-09-30 20:30
- 状态：成功（[OK]，push 成功，最终 commit a399d83）
- 抓取：8 个视频，7 个带字幕（EbP-k9kfqBE 印尼语无字幕，耗时约 2.5 分钟）
- AI 总结：6 个（127AeMh2DFY 罗语 Temu 摩托装备二期实测、2TDl3AbBhoQ 西语母女捏捏乐带货码 kff6759、5t__8fYvw5I 捷克语差评最多商品实测-含被删差评被平台清除的观察、QbPSlaOOdN8 Tibo InShape 法语最烂健身器材-腕器4分卷腹板2分、VUZEfG0ebbE 英语只用 Temu 食材做五星晚餐-牛排好评但餐具套装只有一把叉、PdLEnJlxLEA 西语 Temu 爆款窗式空调-90 天退货+真人客服带货码 kjp6985）
- 剔除噪声：2 个 → exclude:true
  - EbP-k9kfqBE：印尼语家庭重逢 vlog（"temu kangen"=印尼语"见面"，非 Temu 购物），无字幕
  - wU1-6bneE1k：摩洛哥方言出租车司机道德故事，temu 仅 hashtag
- 合并：update_youtube.py 首次 62 个视频，冲突重放后 63 个
- push：先 commit（d83c720）再 pull --rebase 与远端 c0529ab（Actions 06:33 UTC 刷新）冲突，abort 重试一次仍冲突 → 机械解法第六次成功（checkout --ours 远端为底 + rebase --continue + 重跑 update_youtube.py 重放），页面 63 个视频
- 事故与修复：远端 Actions 刷新把昨日 AI 总结视频 rMzBiMlb72A（Tibo InShape）降级回 description（同昨日 4rVBHMnsHgQ 事故，云端保护逻辑不彻底）；从旧 commit fcc27f3 提取该视频对象，用 python 花括号定位+补回 aiSummary/title/summarySource/热评译文，commit a399d83 已推送
- 经验：每次 push 后应 grep 校验全部历史 ai 视频的 summarySource，云端降级事故已连续两天发生，恢复方法=git show 旧 commit 提取 JSON 对象块回补
- 页面最终：summarySource=ai 共 30 条，噪声视频确认不在页面

## 2026-10-01 20:30
- 状态：成功（[OK]，push 成功，最终 commit 86588a4）
- 抓取：8 个视频，6 个带字幕（woH8ikyrdvo 日语巧克力甜品 Shorts TranscriptsDisabled、D9GyGgtcMRI 西语 El Muñe 开箱 无字幕降级），耗时约 3 分钟
- AI 总结：6 个（i0JtDOaeoLI BoostedBoiKyle 5600美元Turbo思域525匹上直线赛、QbPSlaOOdN8 Tibo InShape 腕力器4分卷腹板2分-连续第二天上榜、PdLEnJlxLEA 窗式空调-连续第二天、2bAfrvVoh0I 韩国主播金圣泰与女儿开箱+奇葩外设打游戏、uSLG7dhAmJA 阿语免费码和面机送妈妈、4RApBIZcMvc 波兰双人组畅销榜-吊床/AI眼镜/智能戒指/战术手电）
- 仅翻译：2 个（woH8ikyrdvo、D9GyGgtcMRI）
- 剔除噪声：0 个（当天 8 条全是真实 Temu 内容）
- push：先 commit（6d6b839）再 pull --rebase 与远端 e46f82e（Actions 07:06 UTC 刷新）冲突，abort 重试一次仍冲突 → 机械解法时出事故：checkout --ours 后 rebase --continue 产生空补丁，我们的 commit 被丢弃，随后的 commit --amend 误改写了远端 bot 提交（变成 95ce775），push 被 non-fast-forward 拒绝
- 修复：cp 备份好的 index.html → reset --hard origin/main → 恢复文件 → 重新 commit（f978d65）→ push 成功；随后发现云端又降级了 127AeMh2DFY 的 AI 总结、并把已剔除噪声 U59LwDHDB-E/EbP-k9kfqBE 重新加回页面（云端 re-add 噪声系首次发现）→ 从 a399d83 提取旧对象回补 + 删除两个噪声视频，commit 86588a4 推送成功
- 页面最终：70 个视频，summarySource=ai 共 34 条
- 经验：
  1) 机械解法中 rebase --continue 若本地 commit 成空补丁会被丢弃，之后千万别对 HEAD 做 commit --amend（可能改写远端提交）；改用「备份文件 + reset --hard 远端 + 重新 commit + push」最稳
  2) 云端 Actions 会把此前已剔除的噪声视频重新加回页面（机器翻译标题），每次 push 后噪声校验名单要包含全部历史剔除过的 videoId
  3) 云端降级 AI 总结已连续三天发生（保护逻辑只认 transcript 不认 ai），每次 push 后必须全量 grep 校验历史 ai 视频

## 2026-10-02 20:30
- 状态：成功（[OK]，push 成功，最终 commit 96dbc96）
- 抓取：8 个视频，全部带字幕（约 4 分钟）
- AI 总结：6 个（i0JtDOaeoLI Temu思域换离合器后首上直线赛道-连续第二天、3ZmoMQUUQRs 阿塞拜疆语400马纳特开箱、uSLG7dhAmJA 阿语和面机免费码送妈妈-连续第二天、4RApBIZcMvc 波兰畅销榜-连续第二天、D9GyGgtcMRI El Muñe 摩托边箱（昨日无字幕今日补上总结）、GW7ktkQAt3o 200美元沙发三天后复盘-28日开箱视频续集）
- 剔除噪声：2 个 → exclude:true
  - 5onNmbtq5Uo：阿语/摩洛哥方言突尼斯女孩被拐犯罪故事，temu 仅 hashtag
  - neJAWdLViAk：COD Mobile 抽皮肤视频，"Temu Ghost"是"山寨"俚语，与 Temu 购物无关
- 合并：update_youtube.py 成功，72 个视频（新增/更新 6）
- push：网络两次 SSL 闪断；pull --rebase 确认与远端 86e8d1a（Actions 06:53 UTC）冲突 → 直接用 10-01 稳妥法：reset --hard origin/main + 恢复备份 index.html + 重新 commit（39451b0）+ push 一次成功，全程未进 rebase 冲突态（推荐作为默认流程，比 rebase 机械解法更简单）
- push 后校验发现两处遗留问题（均系云端 Actions 重建页面造成，非本次产生）：
  1) 4 个历史 AI 总结被降级回 description：_xmQWD8CD98、ywE8595N0F8、vr3GDuL1dj4、AbqubLeXVuo → 花括号提取对象从旧 commit（f22cfb1/86e6e25/e10f65b）回补，修复后 ai 总数 41（34+3 新增+4 回补）
  2) 5 个历史噪声被云端加回为完整条目：5hKSjl39voM、XEOORQGckI4、zJoks4O0G1I、RwN8VbmEE88、wU1-6bneE1k → 从页面删除，修复 commit 96dbc96 已推送
- 新踩坑：校验正则 `.{0,400}?summarySource` 会跨对象误报/漏报（transcriptText 很长）；正确做法=花括号配对提取完整对象再查字段。最终用 node/python JSON.parse 整块验证（注意剥离块尾 `};` 与 `/*` 注释）
- 页面最终：67 个视频，summarySource=ai 共 41 条，全部 15 个历史噪声视频确认不在页面

## 2026-10-03 20:30
- 状态：成功（[OK]，push 成功，最终 commit fbaedc8）
- 抓取：8 个视频，全部带字幕（约 1 分钟，本次很快）
- AI 总结：7 个（VIp4XYMw0nE Dr.Ethan Kwan「Amir from Temu」Hinglish 搞笑短剧-配送员角色扮演已注明非购物测评、GW7ktkQAt3o 200美元沙发三天复盘-连续第二天/字幕被自动译成阿语、k7KHVevAz-w 与 1JrjDnZWCg8 Tibo InShape 同日双测俯卧撑板 2 分/支架 7 分、goFKBEVnMXE 乌克兰 Неїжко 20 件厨房用品-草莓切片器崩齿、vfDOv2zCL-s The OtherStuff 福特嘉年华最终集-10镑机盖通风口+120镑CarPlay、pVibmRyTXc4 波兰 Kuba1qba 小玩意合集回归-关税解读+拆三条短合集）
- 剔除噪声：1 个 → exclude:true
  - bCV9rNv1fJ0：印尼语西爪哇省长 KDM 晨间问候视频，"TITIK TEMU"=印尼语「会合点」，词义巧合
- 合并：update_youtube.py 成功，页面 74 个视频（新增/更新 7）
- push：commit（c480e04）后 pull --rebase 与远端 6d7b98e（Actions 06:19 UTC）冲突 → abort 后用 10-01 稳妥法：reset --hard origin/main + 恢复备份 + 重新 commit（fbaedc8）+ push 一次成功，未进 rebase 冲突态
- push 后校验：今日 7 个 ai 全 OK；16 个噪声 videoId（15 历史+今日 bCV9rNv1fJ0）零回归；页面 ai 总数 48（41+7）无降级
- 校验踩坑修正：ai 计数正则要匹配 `"summarySource": "ai"`（冒号带空格），此前模式漏空格导致误报 0；实际分布 48 ai / 15 description / 4 transcript

## 2026-10-04 20:30
- 状态：成功（[OK]，push 成功，最终 commit b8d125f）
- 抓取：8 个视频，7 个带字幕（5YbePSTahbM 日语生ジェラート TranscriptsDisabled 降级描述摘录）
- AI 总结：7 个（VIp4XYMw0nE Amir from Temu 续集-连续第二天、Wk_0qmhes7I Drew 一星vs五星、0Kntn7OYT8Y Dude Life 1000美元充气帐篷生存挑战、k7KHVevAz-w Tibo 俯卧撑板2/10-连续第二天、qGKVHlXHpBY 西语家庭免费码 kkd6388 带货、TI-Np0150no Greg 豪华露营打猎捕鱼+码 KM5358、6kyO0jtZWi8 意语加拉斯科案评论+Temu 赞助段已注明）；1 个仅翻译（5YbePSTahbM，热评指出冰淇淋实为国货只是顺便上 Temu）
- 剔除噪声：0 个（8 条全是真实 Temu 内容）
- 事故与修复：备份 index.html 的时机错了——在 update_youtube 之前备份，冲突恢复时把合并前旧状态推上去，第一推（708295f）实际是今晨 8:30 档本地 run 的数据（我的 AI 总结没上站，且 TI-Np0150no/6kyO0jtZWi8 缺失）；通过 grep 校验发现后重跑 update_youtube 合并 inbox JSON 再推一次（b8d125f）修复
- 关键教训：稳妥法的「备份文件」必须是 update_youtube.py 合并之后的 index.html；push 后必须 grep 校验当日 AI 总结文本确实在页面上
- 云端观察：Actions 今晨按 fetchedAt 滚动清理了 18 个 9-23 前上榜的旧视频（74→60），其中含 4 个带 AI 总结的老视频（_xmQWD8CD98/E9iiFEykA3M/yzBXRezNa7w/PNfl-QetgSc）；属 RETAIN_DAYS=10 滚动窗口策略，非降级事故，不回补
- 页面最终：62 个视频，summarySource=ai 共 49 条（昨日 48 - 云端清理 4 + 新增 5，VIp4XYMw0nE/k7KHVevAz-w 为沿用更新）；16 个历史噪声 videoId 零回归

## 2026-10-05 20:30
- 状态：成功（[OK]，push 成功，最终 commit 985d734）
- 抓取：8 个视频，6 个带字幕（6kyO0jtZWi8 意语加拉斯科、NszDvQEHQ5w 德语 AI 小玩意 无字幕降级描述摘录），耗时约 3.5 分钟；开头有瞬时代理 503 导致 [SKIP] 详情拉取失败提示，但脚本降级后仍选出 8 个并完成全流程，按 [OK] 处理
- AI 总结：4 个（Wk_0qmhes7I Drew 一星vs五星-连续第二天/字幕被自动译成阿语-烤面包机真能烙人像+越野摩托超预期、TI-Np0150no Greg 充气帐篷豪华露营-连续第二天-松鸡狩猎+码 KM5358、qGKVHlXHpBY 西语零元购开箱-连续第二天-码 KKD638、1-6617ujgcs 阿语 Temu 翻车搞笑合集）
- 仅翻译：2 个（6kyO0jtZWi8 沿用昨日 AI 总结未动、NszDvQEHQ5w 无字幕无热评只译标题）
- 剔除噪声：2 个 → exclude:true
  - Kk8kxGXfCmo：摩洛哥方言家庭伦理剧（19 岁女孩怀孕故事），temu 仅 hashtag
  - XpjArY648PI：西语 Roblox 假冒频道打假剧，「TEMU 版我的频道」=山寨俚语，与 Temu 购物无关
- 合并：update_youtube.py 成功，页面 69 个视频（新增/更新 7）
- push：commit（d1d621f）后 pull --rebase 与远端 707ff0d（Actions 06:47 UTC 刷新）冲突 → abort 后用稳妥法（reset --hard origin/main + 恢复 update 后备份 + 重新 commit 985d734 + push）一次成功
- push 后校验：4 条新 AI 总结全部在页面；ai 总数 54（昨日 49 + 新增 5，含沿用更新）；18 个噪声 videoId（16 历史 + 2 今日）零回归
- 流程稳定，无新踩坑

## 2026-10-06 20:30
- 状态：成功（[OK]，push 成功，最终 commit 7410586）
- 抓取：8 个视频，5 个带字幕（R2ImfKqrJx4 塞尔维亚语、1pRaG1rIUbw 捏捏乐 ASMR、ftHT4Qeh5vg 克罗地亚语均 TranscriptsDisabled 降级描述摘录），耗时约 3.5 分钟
- AI 总结：3 个（NszDvQEHQ5w 德语 AI 小玩意-昨日无字幕今日补上总结-1033 欧实测 9 件 AI 产品结论 AI 含量名不副实/3D 打印机实为 Creality、JpBa6dABzAI 英语 31 美元 Temu 求婚戒指情感故事-热评指疑似 AI 生成-已注明非购物测评、d5Awt1IdSnw 乌克兰语校园小物开箱-含战乱无法回家过万圣节背景）
- 仅翻译：3 个（R2ImfKqrJx4 塞语母女 haul、1pRaG1rIUbw 捏捏乐 ASMR、ftHT4Qeh5vg 克罗地亚语秋品 haul 码 kfp3647）
- 剔除噪声：2 个 → exclude:true
  - XpjArY648PI：西语 Roblox 假冒频道剧（连续第二天）
  - 7h6KFkysZyw：摩洛哥方言「sanaa 怀孕」猎奇故事，temu 仅 hashtag
- 合并：update_youtube.py 成功，页面 68 个视频（新增/更新 6）
- push：commit（27e2c8f）后 pull --rebase 与远端 0e7b631（Actions 07:26 UTC 刷新）冲突 → abort 后稳妥法（reset --hard origin/main + 恢复 update 后备份 + 重新 commit 7410586 + push）一次成功
- push 后校验：3 条新 AI 总结全部在页面；近期 AI 视频（Wk_0qmhes7I/TI-Np0150no/qGKVHlXHpBY/1-6617ujgcs/VIp4XYMw0nE/0Kntn7OYT8Y/k7KHVevAz-w）全部保持 ai 无降级；19 个噪声 videoId（18 历史 + 今日 7h6KFkysZyw）零回归；页面 ai 共 53 条（昨日 54，1 条属 10 天滚动窗口自然淘汰，非降级）
- 流程稳定，无新踩坑

## 2026-10-07 20:30
- 状态：成功（[OK]，push 成功，最终 commit 9bc9781）
- 抓取：8 个视频，6 个带字幕（1pRaG1rIUbw 捏捏乐、R2ImfKqrJx4 塞尔维亚语均 TranscriptsDisabled 降级描述摘录），耗时约 2.5 分钟
- AI 总结：4 个（I-QRt_qagNk 英语 1.5 万美元 Temu 折叠小屋-喜剧挑战已注明、_xmQWD8CD98 Temu 翻车合集 P1-2D 印花当 3D 是重灾区、X43Erz10Do8 阿塞拜疆语 Ayka 手机壳/锅具开箱-实体店对比性价比、d5Awt1IdSnw 乌克兰语校园小物开箱-连续第二天-烛热 fondu+巨型笔实测能写）
- 仅翻译：2 个（1pRaG1rIUbw 捏捏乐打分、R2ImfKqrJx4 塞语母女 haul-连续第二天）
- 剔除噪声：2 个 → exclude:true
  - J7N6du3HdJQ：摩洛哥阿拉伯语「女性着装」道德说教视频，temu 仅 hashtag
  - UJ3lrHn0BqQ：波兰语翼骑兵盔甲考古捐博物馆视频，"temu"=波兰语「之前」，词义巧合
- 合并：update_youtube.py 成功，页面 68 个视频（新增/更新 6）
- push：commit（918bb52）后 pull --rebase 与远端 2b4822c（Actions 07:05 UTC）冲突 → abort 后稳妥法（reset --hard origin/main + 恢复 update 后备份 + 重新 commit 9bc9781 + push）一次成功
- push 后校验：4 条新 AI 总结全部在页面（aiSummary 齐）；近期 12 个 AI 视频全部保持 ai 无降级；21 个噪声 videoId（19 历史 + 今日 2，含 YLqImiloSv0 补录）零回归；页面 68 视频 / ai 53 条（含旧 ai 自然滚动淘汰，非降级）
- 校验踩坑修正：页面 JSON 里 videoId 不一定是对象首键，`{"videoId"` 模式抓不到；改为正则定位 `"videoId": "..."` 后 rfind 回溯最近 `{` 再花括号配对，68/53 全对上
- 流程稳定，无新事故

## 2026-10-08 20:30
- 状态：成功（[OK]，push 一次成功，最终 commit 410a839，无冲突未触发稳妥法）
- 抓取：8 个视频，6 个带字幕（-W7c4JkSA7k AgeRestricted、TJTY_W5mtUQ TranscriptsDisabled 降级描述摘录），耗时约 1 分钟
- AI 总结：5 个（kkHltZqxFbU 罗马尼亚语 10 列伊×100 件实测-九成物有所值拟做成系列、X43Erz10Do8 阿语 Ayka 手机壳/浴袍-3-5马纳特壳质感超预期、VFLkGOCO-RA Ayka 七层鞋架 90 马纳特组装、EE5YZq0-ZAE 德语厨房小工具-芒果切片器焊接粗糙吐槽为主、TnvXELThO4w 英语 Katie 迷彩帐篷-无拉链单门/冷凝水严重/仅睡垫同宽）
- 仅翻译：2 个（-W7c4JkSA7k Dope As Yola 420 商品、TJTY_W5mtUQ 克罗地亚语秋装 haul）
- 剔除噪声：1 个 → exclude:true
  - LROBGBZXj5s：英语「TEMU SOLO LEVELING」吐槽山寨动画视频，Temu 为「山寨」俚语，与 Temu 购物无关
- 合并：update_youtube.py 成功，页面 69 个视频（新增/更新 8）
- push 后校验：今日 5 条 AI 总结全部在页面；近期 14 个 AI 视频无降级；22 个噪声 videoId（21 历史 + 今日 1）零回归；页面 ai 共 51 条
- 流程稳定，无新踩坑

## 2026-10-09 20:30
- 状态：成功（[OK]，push 两次成功，最终 commit bd5dc32）
- 抓取：8 个视频，7 个带字幕（TJTY_W5mtUQ 克罗地亚语秋装 haul TranscriptsDisabled 降级描述摘录），耗时约 1 分钟
- AI 总结：5 个（EE5YZq0-ZAE 德语厨房小工具-连续第二天-芒果切片器焊接粗糙+玉米热狗机、vv6dyLyTUiA 日语 Shorts Temu 批量买 20 根 USB 优盘实测无虚标+蓝牙标签打印机、TnvXELThO4w Katie 迷彩帐篷-连续第二天-字幕这次被自动译成阿语-无拉链单门/冷凝水/仅睡垫同宽、cRxxajisgL4 Tibo InShape 法语走步机 150 欧 9/10 高分、GUFuzSDn9TQ Sturmwaffel Shorts 芒果切片器负 5 分 8.28 欧）
- 仅翻译：1 个（TJTY_W5mtUQ 克罗地亚语秋装 haul）
- 剔除噪声：2 个 → exclude:true
  - LROBGBZXj5s：英语「TEMU SOLO LEVELING」山寨动画吐槽（连续第二天）
  - Ii9LrghHMSM：印尼语时政直播（Prabowo 会见 Jokowi），「temu」是印尼语「会面」词义巧合
- 合并：update_youtube.py 成功，页面 67 个视频（新增/更新 6）
- push：commit（0ec2fa0）后 pull --rebase 与远端 af4175a（Actions 07:19 UTC）冲突 → abort 后稳妥法（reset --hard origin/main + 恢复 update 后备份 + 重新 commit 2ce0ca1 + push）一次成功
- push 后校验：今日 5 条 AI 全在页面；噪声 23 个 videoId（22 历史+今日 2，去重后）零回归；发现 6kyO0jtZWi8（意语加拉斯科案）AI 总结被降级为 description（fetchedAt 10-04，历史遗留）→ 从旧 commit b8d125f 提取对象回补，修复 commit bd5dc32 推送成功
- 页面最终：67 个视频，summarySource=ai 共 50 条
- 踩坑记录：index.html 中视频数组变量名是 YOUTUBE_DATA（不是 videos），校验脚本需先定位变量名再花括号配对提取

## 2026-10-10 20:30
- 状态：成功（[OK]，push 两次成功，最终 commit 0658d73）
- 抓取：8 个视频，全部带字幕，耗时约 1 分钟
- AI 总结：6 个（DJUcmfE4qrs Sturmwaffel 面包切割板 13.81 欧-切面不直 3/5 分、cRxxajisgL4 Tibo InShape 走步机 150 欧 9/10-连续第二天、ZSAZCjdq5l0 阿语 Ayka 14 家庭 Vlog-Temu 开箱+便宜窗帘+回应恶评、jI1aBtRSpSQ 主播 Mega 试穿 Temu 服装-裙子勒肋骨娱乐向无结论、6mlYu40r9_0 Sturmwaffel 热狗机 37.6 欧-签太短面衣少 5/10、FoWeKBwtNzE Temu 买 Switch 2 多账号被砍单-港版无封条疑二手）
- 剔除噪声：2 个 → exclude:true
  - Ii9LrghHMSM：印尼语时政直播（Prabowo/Jokowi），「temu」=印尼语「会面」（连续第二天）
  - S6eD8KhE89w：「TEMU MK」街头篮球 1v1，Temu=「山寨」俚语玩梗，与购物无关
- 合并：update_youtube.py 成功，页面 69 个视频（新增/更新 6）
- push：commit（6e18179）后 pull --rebase 与远端 d197ffc（Actions 06:54 UTC）冲突 → abort 后稳妥法（reset --hard origin/main + 恢复 update 后备份 + 重新 commit f7e351a + push）一次成功
- push 后校验：今日 6 条 AI 全在页面；24 个噪声 videoId 零回归；发现 _xmQWD8CD98（Temu 翻车合集 P1）被云端降级为 description → 从昨日 commit bd5dc32 提取对象回补（fc725e7/96d04fe 等旧提交也已降级或 absent，bd5dc32 是最近的好版本），修复 commit 0658d73 推送成功
- 页面最终：69 个视频，summarySource=ai 共 52 条
- 无新踩坑，流程稳定
