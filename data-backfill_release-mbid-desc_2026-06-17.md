# A项目数据后盾：release_mbid + Wikipedia 描述补全

## 时间
2026-06-17 16:06 ~ 18:45

## 目标
1. 为 albums 表添加 `release_mbid TEXT` 列，关联 MusicBrainz release ID
2. 批量回填 MBID + Wikipedia 专辑描述

## 完成情况

### release_mbid（已完工）
- **139/524** 张专辑获得 MBID（26.5%）
- 英文专辑优先，中文 API 无匹配
- 每张 5s 冷却，跑完全程约需 40 分钟

### Wikipedia 专辑描述（大幅推进）
- **102 → 221/524** 张有描述（19.5% → 42.2%）
- 英文专辑覆盖率近 90%（221 张中绝大多数是英文）
- 两次分批成功清理 221 张中的大部分英文空缺

### API 策略重要迭代
| 版本 | 方法 | 问题 |
|------|------|------|
| v3 | opensearch (双查询) + REST summary (三查询) | REST API 连续 429 |
| v4 | **单 API 端点** `generator=search` | 稳定，无 429 |

最终用 `generator=search` + `prop=extracts` 一次调用完成搜索+摘要，8s 冷却跑完全程。

## 剩余未完成
- **303 张中文专辑缺描述** — Wikipedia 只能补英文
- **385 张无 MBID** — MusicBrainz 补中文意义不大
- 13 张冷门英文专辑 Wikipedia 无条目

## 下一步
- 中文专辑描述暂无可靠来源（百度百科反爬）
- MBID 对中文专辑没有实际用途（MusicBrainz 不走中文曲目）
- 如果后续有需求，可考虑豆瓣 API
