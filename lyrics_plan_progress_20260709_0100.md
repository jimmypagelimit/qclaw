# 歌词计划推进报告 - 2026-07-09 01:00

## 执行摘要
cron 自动推进，新增 3 首 LRC 歌词。

## 数据库状态
| 指标 | 数值 | 变化 |
|------|------|------|
| 总曲目 | 5015 | - |
| 有 LRC | 3530 | +3 |
| 整体覆盖率 | 85.0% | +0.1% |
| 缺失 | 752 | -3 |

## 本次执行详情

### 脚本
`_lyrics_cron_batch.py` — 针对高知名度独立乐队批量获取 LRC

### 目标艺术家（LRCLIB 收录率高）
Car Seat Headrest, Big Thief, Sufjan Stevens, The National,
Phoebe Bridgers, Mitski, Bon Iver, Arcade Fire, Radiohead, LCD Soundsystem 等

### 处理结果（40 首样本，截于 74s 时间限制）
| 结果 | 数量 |
|------|------|
| 成功获取 | 3 |
| LRCLIB 无同步歌词 | 4 |
| API 超时/编码错误 | 3 |

### 成功获取
1. Big Thief - Masterpiece
2. Car Seat Headrest - KS (Replaced with Cute Thing)
3. Car Seat Headrest - The Hard Part (Sober to Death demo)

### 失败原因分析
- Sufjan Stevens 超长曲名编码错误（Unicode apostrophe `'`）
- Big Thief 部分歌曲 LRCLIB 无同步歌词（可能有纯文本）
- API 超时（8s timeout 偏长）

## 当前最大缺口（Top 10）
| 艺人 | 缺失 LRC | 备注 |
|------|---------|------|
| The Cure | 60 | 大量 demo/bootleg，难以获取 |
| John Lennon | 37 | 非核心音乐库 |
| 王菲 | 26 | LRCLIB 无收录 |
| Funeral Mist | 26 | 黑金属，极少收录 |
| Tizzy Bac | 21 | 中文/LRCLIB 有限 |
| 赵季平 | 20 | 影视配乐，无歌词 |
| 陈升 | 19 | 中文/LRCLIB 有限 |
| 戴佩妮 | 19 | 中文 |
| 刀郎 | 19 | 中文 |
| Carsick Cars | 18 | 中文独立 |

## 系统限制
- **QEMU 时间限制**: ~90s，需控制在 80s 内
- **LRCLIB API**: 单次查询 8s 超时，影响吞吐量
- **中文歌曲**: LRCLIB 收录率 < 5%，需其他方案

## 结论
增量推进有效但缓慢（每次 +3 首）。剩余 752 首缺失中，大部分是：
1. 中文歌曲（需网易云 API）
2. 冷门/demo/bootleg 版本（客观缺失）
3. 器乐曲目（无歌词）

建议：接受 85% 覆盖率，或投入更多时间开发中文歌词获取方案。
