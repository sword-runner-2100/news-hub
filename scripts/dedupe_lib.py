#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新闻去重工具 —— update_news.py（增量）与 dedupe_news.py（存量清洗）共用。

为什么需要这么复杂：
    只按 url 去重是不够的。Google 源的链接是加密中转地址
    （news.google.com/rss/articles/CBMi...），同一篇文章换个关键词或市场抓回来 url 就变了。
    结果就是同一事件反复入库 —— 实测全站 168 条里有 48 条是重复。

    按标题精确匹配也不够，因为翻译接口不是确定性的，同一篇报道会译出不同中文。

    最终方案是「精确键 + 相似度兜底」，相似度用 2-gram 的 overlap 系数。
"""

import re

# 判定为「同一事件」的相似度阈值。
#
# 实测样本（2-gram overlap = 交集 / 较小的那个集合，已剔除超长英文专名）：
#     同一事件的不同译法 / 不同媒体报道   0.46 ~ 0.82
#     同主题但确实是两条新闻             0.42（HOMM3「引擎重构」vs「官方实机」）
#                                        0.46（gamescom「公布阵容」vs「社区回顾」）
#     只是共享品牌名或游戏名的不同新闻     0.00 ~ 0.29
#
# 取 0.45 卡在上面两类之间。宁可漏合并（读者多看到一条重复）也不要误杀
# （真的丢掉一条新闻）—— 漏了还能再清，误删就找不回来了。
#
# 已知边界：0.46 附近的「同主题不同事件」仍会被合并，比如 gamescom 的
# 「育碧公布直播阵容」与「ATOMEGA 社区休息室回顾」。15 个实测样本里就这一例，
# 且丢的是低价值条目，为它把阈值抬到 0.47 反而会漏掉更多正确合并，故维持现状。
SIM_THRESH = 0.45


def title_key(t):
    """标题精确去重键：去标点空格后取前 40 字。"""
    return re.sub(r"[\s\W_]+", "", str(t or "")).lower()[:40]


def grams(t, n=2):
    """标题的字符 n-gram 集合。

    用字符而非词，是因为中文标题没有空格分词，且字符 n-gram 对语序不敏感 ——
    「Temu 与 Poşta Română 签署…」和「Poşta Română 与 Temu 签署…」
    是同一条新闻，按词或前缀都对不上，按字符 n-gram 则高度重合。

    计算前会先剔除超长英文串（见 _strip_long_en）。
    """
    s = re.sub(r"[\s\W_]+", "", str(t or "")).lower()
    s = _strip_long_en(s)
    return {s[i:i + n] for i in range(len(s) - n + 1)} or {s}


# 超长英文专名（归一化后 25 个字符以上）。
#
# 必须剔除，否则会误杀：像 "Assassin's Creed Black Flag Resynced" 归一化后有 31 个字符，
# 单它一个就贡献了几十个 gram，导致同一款游戏的两条不同新闻
# （「更新 1.0.7 发布」vs「传言将登陆 Switch 2」）相似度冲到 0.66 被判为重复。
#
# 只剔除「超长」的，短专名要保留 —— Temu、Ubisoft、Poşta Română 这些是区分事件的
# 关键特征，剔掉后「Temu 与罗马尼亚邮政签署协议」和「Poşta Română 与 Temu 达成合作」
# 就对不上了。25 这个长度足够把「游戏全名」和「品牌名」区分开。
_LONG_EN = re.compile(r"[a-z0-9]{25,}")


def _strip_long_en(s):
    return _LONG_EN.sub("", s)


def similarity(a, b):
    """两个标题的相似度，用 overlap 系数（交集 / 较小集合）。

    不用 Jaccard（交集 / 并集）是因为它惩罚长度差：同一事件的两条报道常常一长一短
    （「…提供物流服务的谅解备忘录」35 字 vs 「…签署合作伙伴关系」24 字），
    Jaccard 只有 0.275，而 overlap 有 0.483 —— 后者才如实反映「短的那条基本被长的包含」。
    """
    ga, gb = grams(a), grams(b)
    denom = min(len(ga), len(gb))
    if not denom:
        return 0.0
    return len(ga & gb) / denom


def similar(a, b, thresh=SIM_THRESH):
    return similarity(a, b) >= thresh


class SimilarIndex:
    """按 2-gram 建的倒排索引，用于在一堆标题里快速找出重复项。

    倒排是为了避免 O(n²)：只对「至少共享一个 gram」的候选做精确计算。
    """

    def __init__(self):
        self.items = []
        self.inv = {}      # gram -> [下标, ...]
        self.by_key = {}   # title_key -> 下标

    def add(self, item):
        i = len(self.items)
        self.items.append(item)
        k = title_key(item.get("title") or "")
        if k:
            self.by_key.setdefault(k, i)
        for g in grams(item.get("title")):
            self.inv.setdefault(g, []).append(i)
        return i

    def find_by_key(self, title):
        """精确匹配：标题归一化后完全一致。"""
        k = title_key(title)
        if not k or k not in self.by_key:
            return None
        return self.items[self.by_key[k]]

    def find_similar(self, title, topic=None):
        """模糊匹配：找出描述同一事件的已有条目（没有则 None）。"""
        ga = grams(title)
        cnt = {}
        for g in ga:
            for i in self.inv.get(g, []):
                cnt[i] = cnt.get(i, 0) + 1
        best, best_s = None, 0.0
        for i, shared in cnt.items():
            other = self.items[i]
            if topic is not None and other.get("topic") != topic:
                continue
            denom = min(len(ga), len(grams(other.get("title"))))
            if not denom:
                continue
            s = shared / denom
            if s >= SIM_THRESH and s > best_s:
                best, best_s = other, s
        return best

    def find(self, title, topic=None):
        """先精确后模糊，返回与之重复的已有条目。"""
        return self.find_by_key(title) or self.find_similar(title, topic)
