# RYM Expert 深化增强计划（2026-06-13）

## 目标
将 RYM 抓取能力从「单张专辑搜索」升级到「系统化数据管道」，支撑：
- 专辑评分回填（类似 PF）
- 流派树系统爬取
- Charts 榜单自动监控
- 收藏对比推荐

## 当前资产
| 文件/目录 | 状态 | 说明 |
|----------|------|------|
| `data/charts-yearly/*.json` | ✅ 已有 | 2020-2025 年度榜数据 |
| `data/new-releases/*.json` | ✅ 已有 | 新发片监控 |
| `data/collection/gap_*.json` | ✅ 已有 | 收藏对比分析 |
| `rym_tool.py` | ✅ 可用 | CloakBrowser 单专辑抓取 |
| `docs/*.md` | ⚠️ 缺失 | 无 INDEX/KB 文档 |

## 核心增强项

### 1. 统一 CLI 工具
**目标**：一个命令搞定所有 RYM 操作
```bash
python rym_cli.py search "专辑" "艺人"
python rym_cli.py charts --year 2026
python rym_cli.py genre-tree rock
python rym_cli.py fill-db --limit 50
```

**关键能力**：
- CloakBrowser 自动管理（launch → home → wait CF → navigate）
- 重试逻辑（CF 拦截检测：文件大小 < 73KB）
- 结果缓存（避免重复抓取）

### 2. 数据库回填管道
**目标**：RYM 评分 → `_music_latest.db`
- 新增字段：`rym_rating`, `rym_ratings_count`, `rym_url`
- 命中策略：英文名优先 + 专辑名模糊匹配
- 批量模式：`--limit N` 控制数量，heartbeat 自动推进

### 3. 流派树爬取系统
**目标**：系统遍历 Metal/Folk/Electronic 等
- 入口：`/genre/{slug}/`
- 提取：所有子流派链接 + 名称
- 存储：JSON 树形结构 → Markdown 知识库

**已知问题**：
- `/genre/` 首页是卡片目录，不是树
- `page_features_secondary_metadata_genres_*` 是「相关流派」不是子流派
- 需要找到真正的子流派区域（可能需展开「Hierarchy」）

### 4. Charts 监控自动化
**目标**：每日自动抓取新发片 + 年度榜更新
- cron 任务：`rym-charts`（每 3 小时）
- 存储路径：`data/charts-yearly/{year}/{year}.json`
- 增量更新：只抓新页，不重复

### 5. 知识库体系
**目标**：所有 RYM 数据 → 可查 Markdown
- `docs/INDEX.md` — 导航
- `docs/GENRES-KB.md` — 流派树知识库
- `docs/CHARTS-KB.md` — 榜单汇总
- `docs/NEW-RELEASES-KB.md` — 新发片动态

## 技术约束
1. **CloakBrowser 必须**：普通 Playwright 被 CF 识别
2. **location.href 代替 page.goto**：直接跳转被 503
3. **首页等待 20-30 秒**：CF challenge 完成需时间
4. **GBK 编码问题**：控制台打印中文/emoji 会报错
5. **headless=False**：无头模式被 CF 检测

## 执行优先级
1. **P0**：统一 CLI + 数据库回填（立即可用）
2. **P1**：流派树爬取（需要定位子流派区域）
3. **P2**：Charts 自动化（已有数据，增量即可）
4. **P3**：知识库文档（数据稳定后整理）

## 预期产出
- `rym_cli.py` — 统一命令行工具（200+ 行）
- `rym_db_bridge.py` — 数据库回填管道（150+ 行）
- `rym_genre_tree.py` — 流派树爬取（100+ 行）
- `docs/INDEX.md` — 知识库导航
- 新增数据库字段：`rym_rating`, `rym_ratings_count`, `rym_url`
