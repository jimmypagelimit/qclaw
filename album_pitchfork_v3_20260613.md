# 2026-06-13 Pitchfork Expert v3.0 深化

## 目标
深化 Pitchfork 网站功能，修复 v2 的 bug（评分提取、BNM 标记、大量 null 字段）。

## 关键发现
Pitchfork 已从 `__NEXT_DATA__` 迁移到 `window.__PRELOADED_STATE__`。所有结构化数据（评分、BNM、艺人、流派、厂牌、日期、作者、简介、封面图）均可通过纯 HTTP + JSON 解析获取，**无需浏览器**。

## 完成工作

### pf_scraper.py v3.0
- 纯 Python（urllib + json + re），无需 CloakBrowser/opencli
- 数据源：`__PRELOADED_STATE__` → `transformed.review.headerProps.*`
- 关键字段路径：
  - 评分: `headerProps.musicRating.score`
  - BNM: `headerProps.musicRating.isBestNewMusic`
  - 艺人: `headerProps.artists[0].name`（⚠️ 不是 artistDetails）
  - 专辑: `headerProps.dangerousHed`（需去 HTML 标签）
  - 流派: `headerProps.infoSliceFields.genre`
  - 厂牌: `headerProps.infoSliceFields.label`
  - 作者: `coreDataLayer.content.authorNames`
  - 简介: `headerProps.dangerousDek`
- 搜索功能：`/search/?q=xxx` 的 `__PRELOADED_STATE__` 按分类（艺人/专辑评论/单曲/文章/新闻）返回

### 验证结果
- 20/20 最新评论批量抓取 100% 成功（0 error）
- Car Seat Headrest 搜索返回全部 7 张专辑
- 每条记录完整度：评分/BNM/艺人/专辑/流派/厂牌/年份/日期/作者/简介/封面

### RYM Slacker Rock 翻译
- 正确 slug：`slacker-rock`（连字符，非下划线）
- 已存入 `rym_genre_translations/slacker-rock.md`

## Git
- Commit: 5e9e897, pushed to main
