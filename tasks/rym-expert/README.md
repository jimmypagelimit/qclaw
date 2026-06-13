# RYM Expert 项目

> 深化增强版 RYM 抓取能力

## 项目结构

```
tasks/rym-expert/
├── rym_cli.py           # 统一 CLI 工具
├── rym_db_bridge.py     # 数据库回填管道
├── rym_kb_builder.py    # 知识库生成器
├── data/
│   ├── charts-yearly/   # 年度榜单数据
│   ├── collection/      # 收藏对比数据
│   └── new-releases/    # 新发片数据
└── docs/
    └── RYM-KB.md        # RYM 知识库
```

## 已实现功能

### 1. 专辑搜索 ✅
基于 `rym_tool.py`（CloakBrowser + JS click 绕 CF）
- 单张专辑搜索：`python rym_tool.py "专辑名" "艺人名"`
- 输出：JSON + 截图

### 2. 数据库回填 ⚡
- 目标：`_music_latest.db`
- 字段：`rym_rating`, `rym_ratings_count`, `rym_url`
- 覆盖率：101/520（19.4%）

### 3. 知识库生成 📚
- `docs/RYM-KB.md` — RYM 高分榜 Top 50
- 自动统计覆盖率

### 4. 数据积累 📊
- 年度榜单：2020-2025（约 300+ 条）
- 新发片监控
- 收藏对比分析

## 待实现功能

### 1. 流派树爬取 🌳
- 入口：`/genre/{slug}/`
- 目标：Metal/Folk/Electronic 等
- 已知问题：子流派区域定位失败

### 2. Charts 自动化 📈
- cron 任务：每 3 小时抓取
- 增量更新

### 3. 艺人碟库 🎸
- 收藏对比推荐
- 缺失高分专辑推荐

## 技术约束

1. **CloakBrowser 必须**：普通 Playwright 被 CF 识别
2. **headless=False**：无头模式被检测
3. **首页等待 20-30 秒**：CF challenge 完成需时间
4. **location.href 绕 CF**：直接 `page.goto()` 会被 503
5. **GBK 编码问题**：控制台无法打印中文/emoji

## 快速开始

```bash
# 搜索专辑
python rym_tool.py "Twin Fantasy" "Car Seat Headrest"

# 回填数据库（前50张）
python rym_db_bridge.py --limit 50

# 生成知识库
python rym_kb_builder.py
```

## 参考资料

- [TOOLS.md](../../TOOLS.md) — 技术细节
- [PLAN.md](PLAN.md) — 深化计划
