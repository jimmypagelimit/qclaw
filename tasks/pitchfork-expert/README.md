# Pitchfork Expert — 项目文档

## 概述

从 Pitchfork 批量抓取专辑评论数据（评分、BNM、艺人、流派、厂牌、日期、作者、简介、封面）。

**核心发现**：Pitchfork 已移除 `__NEXT_DATA__`，改用 `window.__PRELOADED_STATE__`。所有结构化数据均可通过纯 HTTP + JSON 解析获取，**无需浏览器**。

## 数据源

| 页面类型 | URL 模式 | 数据提取方式 |
|----------|----------|-------------|
| 专辑列表 | `/reviews/albums/` | JSON-LD `ItemList` |
| 评论详情 | `/reviews/albums/{slug}` | `__PRELOADED_STATE__` JSON |
| 搜索结果 | `/search/?q=xxx` | `__PRELOADED_STATE__` JSON（分类结构） |

## 脚本

**`pf_scraper.py` v3.0** — 主脚本，纯 Python（urllib + json + re），无需浏览器。

### 用法

```bash
# 最新专辑列表（默认首页）
python pf_scraper.py --limit 10

# 多页抓取
python pf_scraper.py --pages 3 --limit 30

# 搜索艺人
python pf_scraper.py --search Car+Seat+Headrest --limit 5

# 只看列表（不抓详情页）
python pf_scraper.py --search Car+Seat+Headrest --list-only

# 指定输出文件
python pf_scraper.py --limit 20 --output my_reviews.json
```

### 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--limit` | 10 | 抓取详情页的最大数量 |
| `--pages` | 1 | 列表页数 |
| `--search` | — | 搜索关键词（空格用+号） |
| `--list-only` | false | 只输出列表，不抓详情 |
| `--output` | 自动生成 | 输出 JSON 文件名 |

## 输出字段

| 字段 | 来源 | 说明 |
|------|------|------|
| `pitchfork_score` | `headerProps.musicRating.score` | 编辑评分（0-10） |
| `bnm` | `musicRating.isBestNewMusic` | Best New Music |
| `bnr` | `musicRating.isBestNewReissue` | Best New Reissue |
| `artist` | `headerProps.artists[0].name` | 艺人名 |
| `album` | `headerProps.dangerousHed` | 专辑名（已去HTML标签） |
| `genre` / `genres` | `infoSliceFields.genre` | 流派（支持多流派/分隔） |
| `label` | `infoSliceFields.label` | 厂牌 |
| `release_year` | `infoSliceFields.releaseYear` | 发行年份 |
| `review_date` | `infoSliceFields.reviewDate` | 评论日期 |
| `author` / `author_names` | `coreDataLayer.content.authorNames` | 作者 |
| `dek` | `headerProps.dangerousDek` | 评论简介 |
| `image_url` | JSON-LD `itemReviewed.image` | 封面图 |
| `url` | — | 评论页 URL |

## 已验证

- ✅ 20/20 最新评论批量抓取成功（0 error）
- ✅ Car Seat Headrest 搜索返回全部 7 张专辑评论
- ✅ 评分/BNM/艺人/流派/厂牌/日期/作者/简介 全部正确
- ✅ 纯 HTTP，无需 CloakBrowser 或 opencli

## 已知限制

- `reader_score` / `reader_count`：`__PRELOADED_STATE__` 中未包含，需要 JS 渲染后的 DOM
- 多作者评论：`authorNames` 是逗号分隔字符串
- `search` 的分页：需要后续验证

## 版本历史

- **v1.0**: opencli + CDP 浏览器方案（慢、不稳定）
- **v2.0**: `__NEXT_DATA__` JSON 提取（Pitchfork 已移除）
- **v2.1**: 修复 album 名提取、BNM 回退
- **v3.0**: `__PRELOADED_STATE__` 纯 HTTP 方案，搜索功能整合
