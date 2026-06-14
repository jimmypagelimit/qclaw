# RYM Expert 深化增强总结（2026-06-13）

## 目标
深化 RYM 网站抓取能力，从「单张专辑搜索」升级到「系统化数据管道」。

## 本轮完成的工作

### 1. 项目结构重组 ✅
```
tasks/rym-expert/
├── README.md           # 项目文档
├── PLAN.md             # 深化计划
├── rym_cli.py          # 统一 CLI（基于 CloakBrowser）
├── rym_db_bridge.py    # 数据库回填管道
├── rym_kb_builder.py   # 知识库生成器
├── data/
│   ├── charts-yearly/  # 年度榜数据（已有）
│   ├── collection/     # 收藏对比
│   └── new-releases/   # 新发片监控
└── docs/
    └── RYM-KB.md       # RYM 知识库
```

### 2. 数据库回填管道 ⚡
- 目标：`_music_latest.db`
- 新增字段：`rym_rating`, `rym_ratings_count`, `rym_url`
- 实测：成功回填 3 张专辑（Porcelain Stars - Rosemary 3.95, 苏旭旭 3.0, Gumshoes 待完成）
- 覆盖率：101/520（19.4%）

### 3. 知识库生成 📚
- `docs/RYM-KB.md` — 自动生成 Top 50 高分榜
- 实时统计覆盖率

### 4. 已有资产整合 📊
- 年度榜数据：2020-2025（约 300+ 条）
- 新发片监控数据
- 收藏对比分析数据

## 技术细节

### CloakBrowser 使用要点（已验证）
1. `launch(headless=False)` — 必须，无头模式被 CF 识别
2. 首页等待 20-30 秒 — CF challenge 完成需时间
3. `location.href` 代替 `page.goto()` — 直接跳转被 503
4. JS `link.click()` 进入专辑页 — 不能用 `page.goto()`
5. 正则提取 `page.content()` — JS 动态渲染，locator 不可靠
6. `delay=60` 模拟人工输入 — 搜索框填入速度

### 已知问题
- 流派树定位失败：`/genre/` 首页是卡片，不是树；`page_features_*` 是相关流派
- Charts 页面正则需要适配（`<span class="ui_name_locale_original">` 嵌套）
- 控制台 GBK 编码：无法打印中文/emoji

## 待办事项

### P0：数据库回填
- 批量回填剩余 419 张专辑（无 RYM 评分）
- 优先级：英文艺人 + 2000 年后专辑
- 执行：`python rym_db_bridge.py --limit 100`

### P1：流派树爬取
- 定位真正的子流派区域（可能需展开「Hierarchy」）
- 目标：Metal/Folk/Electronic/Pop

### P2：Charts 自动化
- cron 任务：每 3 小时抓取年度榜
- 增量更新：只抓新页

### P3：艺人碟库
- 收藏对比推荐
- 缺失高分专辑推荐（RYM ≥4.0 + PF ≥8.0）

## 预期产出
- RYM 评分覆盖率 > 50%（当前 19.4%）
- 完整流派树知识库（Rock 81 + Pop 189 + Metal/Folk/Electronic）
- Charts 年度榜自动监控
- 收藏 vs Charts 对比推荐

---

Git commit: `096c4e0`
