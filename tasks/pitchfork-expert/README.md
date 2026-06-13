# Pitchfork Expert — 项目定位

## 核心价值

Pitchfork 是乐评，不是数据库。它的价值在于**专业乐评人对音乐的解读**，而不是艺人名、发行年、厂牌这些基本信息——那些 MusicBrainz/Discogs 做得好得多。

## 项目基调

**围绕三个核心：**

### 1. 评分（已完成）
- 编辑评分 / BNM / BNR
- 历史评分分布分析

### 2. 评论全文翻译
- 重量级专辑的完整评论正文
- 翻译后存入知识库，供日后参考
- 重点：8.5+ 高分评论、历史名评（如 BNM 经典）

### 3. 榜单知识库
- 各年代 All-Time Top 专辑（1970s–2020s）
- 年度 Best Albums 榜单
- Pitchfork 评分算法分析（为什么他们给某张专辑打高分/低分）

## 不做的事

❌ 艺人信息 / 发行年 / 厂牌 / 流派分类  
这些是 MusicBrainz/Discogs 的领域，不重复造轮子。

## 技术方案

- 纯 HTTP + `__PRELOADED_STATE__`（无需浏览器）
- 评论正文：从 HTML `<div class="article-content">` 或 `__PRELOADED_STATE__` 提取
- 年代榜单：爬取 `/best/albums/{year}/` 等页面

## 输出形式

- `docs/scores-KB.md` — 评分知识库
- `docs/reviews/{slug}.md` — 翻译后的评论原文+译文
- `docs/charts-KB.md` — 年代/年度榜单
