# Pitchfork Expert 深化探索（2026-06-13）

## 目标
继续深化 Pitchfork 抓取能力，建立从搜索到知识库的完整管道。

## 本轮完成的工作

### 1. 数据库集成管道 ✅
- `pf_db_bridge.py` — 搜索+评分回写一体化工具
- `pf_batch_v2.py` — 智能批量搜索（只查英文艺人+2000年后专辑）
- `pf_kb_builder.py` — 评分知识库自动生成
- 数据库新增字段：`pitchfork_score` (REAL) + `review_url` (TEXT)

### 2. 评分入库结果
- **20 张专辑**已有 PF 评分
- **12 张 BNM**（≥8.0）
- 最高分：Aldous Harding — Train on the Island (9.0)
- CSH 完整评分链：Twin Fantasy 8.6 → Teens of Denial 8.5 → Teens of Style 8.1 → Nervous Young Man 8.0 → How to Leave Town 8.0 → MADLO 6.6

### 3. 核心脚本体系
| 脚本 | 功能 |
|------|------|
| `pf_scraper.py` | v3.0 纯 HTTP 评论抓取（搜索+详情） |
| `pf_review_body.py` | 评论正文 IR→Markdown 提取翻译 |
| `pf_db_bridge.py` | 数据库回写管道 |
| `pf_kb_builder.py` | PF-SCORES-KB.md 知识库生成 |
| `pf_list_scraper.py` | 年代榜单抓取（best-of 页面 404，待调试） |

### 4. 已生成知识库
- `docs/PF-SCORES-KB.md` — 评分排行榜
- `docs/reviews/` — 3 条评论摘要（Teens of Style, Bitknot, Beauty Land）
- `docs/en/zh/` — Twin Fantasy + Teens of Denial 英中双语翻译

### 5. 修复的错误
- 删除 4 条中文假阳性 PF 评分（album_id 3/4/5/348 硬编码错误匹配）
- 设置正确 CSH PF 评分（323/382/383/386/384）
- `pitchfork_score` 数据库字段新增完成

### 6. 已知问题
- **年代榜单页面**：`/best/albums/2024/` 返回 404，Pitchfork 已改版
- **SSL 问题**：Python urllib 不稳定，用 curl subprocess 绕过
- **GBK 编码**：控制台输出 emoji/中文仍是问题
- **剩余 134 张英文艺人专辑**无 PF 评分待补

## 决策
- 不抓年代榜单而是直接评分匹配（更高效，更有用）
- 中文艺人放弃 PF 搜索（Pitchfork 不覆盖华语音乐）
- 评分知识库采用 DB → KB 的自动化管道，而非手动整理
