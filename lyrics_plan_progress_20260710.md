# 歌词计划推进报告 - 2026-07-10 08:46

## 数据库状态

| 指标 | 数值 | 覆盖率 |
|------|------|--------|
| 总曲目 | 5015 | — |
| 有 LRC | 3531 | 70.4% |
| 有任意歌词 | 4264 | 85.0% |
| 缺失 | 751 | 15.0% |

本次执行：成功 +1（Car Seat Headrest - The Ballad of the Costa Concordia）

## 剩余缺口分析（Top 10）

| 艺人 | 缺失 | 原因 |
|------|------|------|
| Funeral Mist | 26 | 黑金属，LRCLIB 不收录 |
| The Cure | 25 | 大部分为 demo/bootleg 特殊版本 |
| 赵季平 | 19 | 影视配乐，无歌词 |
| John Lennon | 17 | 部分版本 LRCLIB 无收录 |
| 陈升 | 15 | 中文歌曲 |
| Maria BC | 11 | 独立乐队，部分冷门 EP |
| Blood At Ease | 11 | 独立乐队 |
| 葬尸湖 | 9 | 中文黑金属 |
| 深山 | 9 | 中文黑金属 |
| Tizzy Bac | 9 | 中文独立 |

## 缺口特征总结

剩余 751 首缺失可分三类：

1. **中文歌曲（约 35%）** — 葬尸湖、深山、陈升、carsick cars 等，LRCLIB 不收录中文内容，需网易云 API
2. **冷门/非主流（约 35%）** — Funeral Mist 黑金属、Maria BC 冷门 EP、器乐曲目
3. **Bootleg / Demo / 特殊版本（约 30%）** — The Cure demo、Car Seat Headrest 替换版本等

## 系统问题修复

- **Cron 投递错误**：修复 `--channel feishu`，下次起效

## 结论

85% 覆盖率基本触及 LRCLIB 的上限。继续增量推进每天约 +1 首（高匹配艺人剩余曲目多为 alternate versions）。

剩余 15% 缺口中文部分需网易云 API，英文冷门部分客观缺失（非歌词管道问题）。

---

**建议：** 歌词计划可以降频为每周一次，或接受当前覆盖率。
