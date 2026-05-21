# 专辑数据库 - 项目文档

## 核心业务逻辑：双表同步 ⭐

所有写操作（新增/收听/编辑/删除）**必须同时操作年份表和总表**。

### 数据库结构

| 表 | 含义 | 说明 |
|---|---|---|
| `albums` | 总库 | 所有年份的完整汇总 |
| `albums_2024` | 2024年表 | 2024年收听/入库的专辑 |
| `albums_2025` | 2025年表 | 2025年收听/入库的专辑 |
| `albums_2026` | 2026年表 | 2026年收听/入库的专辑 |

### 跨表关联规则

- **关联键**：`album_name + artist`（不同表的 `album_id` 独立，不能跨表用 id 关联）
- **判重依据**：同一张专辑在两张表里用 `album_name + artist` 判断是否为同一条记录

### 写操作规则

#### 新增专辑
1. 写入指定年份表（如 `albums_2026`）
   - 已存在（album_name + artist 匹配）→ 只 `total_listen_count + 1`
   - 不存在 → 插入新记录
2. 写入 `albums` 总表
   - 已存在 → 只 `total_listen_count + 1`
   - 不存在 → 插入新记录

#### 收听 +1
1. 更新年份表 → 找到专辑 `total_listen_count + 1`（不存在则新增）
2. 更新 `albums` 总表 → 找到专辑 `total_listen_count + 1`

#### 编辑专辑
1. 更新当前表
2. 通过 `album_name + artist` 找到另一张表的对应记录，同步更新

#### 删除专辑
1. 删除当前表的记录
2. 通过 `album_name + artist` 找到另一张表的对应记录，同步删除
3. 如果从总表删除，需要同步删除**所有**年份表中的对应记录

### 统计规则

| 查询类型 | 查哪张表 |
|---------|---------|
| 总排行 | `albums` |
| 年度排行 | `albums_YYYY`（用 `--year` 指定） |
| 仪表盘统计 | `albums`（风格/国家分布） |

---

## UI 设计风格指南 ⭐

**风格方向：Editorial / Magazine**

这是用户确认并喜欢的风格，后续所有 UI 修改必须保持这个方向。

### 字体

| 用途 | 字体 | 备选 |
|------|------|------|
| **标题** | Cormorant Garamond | Georgia, serif |
| **正文** | IBM Plex Sans | -apple-system, BlinkMacSystemFont, sans-serif |
| **数字** | Cormorant Garamond | — |

字体加载（在 `<head>` 中）：
```html
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap" rel="stylesheet">
```

**禁止使用**：Inter、Arial、Roboto、系统默认无衬线字体作为标题字体。

### 颜色

| 变量 | 值 | 用途 |
|------|---|------|
| `--bg` | `#ffffff` | 页面背景 |
| `--text` | `#1a1a1a` | 主文字 |
| `--accent` | `#1a3a52` | 主色（深海军蓝） |
| `--text-secondary` | `#555` | 次级文字 |
| `--text-muted` | `#888` | 弱化文字 |
| `--border` | `#e5e5e5` | 边框 |

**禁止使用**：深色主题、高饱和度荧光色、渐变背景。

### 排版

- **大标题**：42px / font-weight 600 / letter-spacing -0.03em（Cormorant Garamond）
- **章节标题**：28px / font-weight 600
- **正文**：15px / line-height 1.65（IBM Plex Sans）
- **标签/小字**：11-12px / uppercase / letter-spacing 0.08-0.1em
- **统计数字**：48px / font-weight 600（Cormorant Garamond）

### 留白

- 容器 padding：`56px 48px`
- 卡片 padding：`24-32px`
- 元素间距：`20-32px`
- 大量呼吸空间，不要挤在一起

### 动画

- **页面切换**：`fadeIn` 0.6s，translateY(12px) → 0
- **统计卡片**：staggered reveal，每张间隔 0.05s
- **卡片 hover**：translateY(-2px) + box-shadow 增强
- **排行榜 hover**：padding-left 增大（滑动效果）
- **弹窗**：slideUp 0.4s，scale(0.96) → 1
- **所有过渡**：200ms cubic-bezier(0.4, 0, 0.2, 1)

### 视觉元素

- 卡片顶部装饰线：hover 时从左到右展开（scaleX(0) → 1）
- 统计卡片 `.highlight` 装饰线常驻显示
- 导航 active 状态：底部小圆点
- 圆角：12px（卡片）、6px（按钮/输入框）
- 阴影：极淡，rgba(0,0,0,0.04-0.1)

### 响应式断点

| 断点 | 变化 |
|------|------|
| ≤ 1024px | 统计卡片 2 列 |
| ≤ 768px | 统计卡片 1 列、图表单列、表单单列、排行榜隐藏 bar |

---

## 封面存储 ⭐

**路径**：`album-tracker/covers/`

数据库 `cover_image_url` 字段存储相对路径（如 `covers/01-Car_Seat_Headrest-Twin_Fantasy.jpg`）。

### 封面来源优先级

1. **iTunes Search API** — 主力，600x600，覆盖主流专辑
2. **Deezer API** — 中文专辑补充（网易云无但 Deezer 有的）
3. **网易云 API** (`music.163.com/api/search`) — 中文独立/地下乐队（葬尸湖等）
4. **MusicBrainz Cover Art Archive** — 备选（SSL 不稳定时跳过）

### 已下载封面（总榜 Top 10）

| 排名 | 专辑 | 艺术家 | 来源 | 文件 |
|------|------|--------|------|------|
| 1 | Twin Fantasy | Car Seat Headrest | iTunes | 01-Car_Seat_Headrest-Twin_Fantasy.jpg |
| 2 | 不允许哭泣的场合 | 魏如萱 | iTunes | 02-魏如萱-不允许哭泣的场合.jpg |
| 3 | Disintegration | The Cure | iTunes | 03-The_Cure-Disintegration.jpg |
| 4 | Ziggy Stardust | David Bowie | iTunes | 04-David_Bowie-The_Rise_and_Fall_of_Ziggy_Sta.jpg |
| 5 | 优雅的刺猬 | 魏如萱 | iTunes | 05-魏如萱-优雅的刺猬.jpg |
| 6 | In the Aeroplane Over the Sea | Neutral Milk Hotel | iTunes | 06-Neutral_Milk_Hotel-In_the_Aeroplane_Over_the_Sea.jpg |
| 7 | Funeral | Arcade Fire | iTunes | 07-Arcade_Fire-Funeral.jpg |
| 8 | 弈秋 | 葬尸湖 | 网易云 | 08-葬尸湖-弈秋.jpg |
| 9 | 孤雁 | 葬尸湖 | 网易云 | 09-葬尸湖-孤雁.jpg |
| 10 | 珍珠刑 | 魏如萱 | Deezer | 10-魏如萱-珍珠刑.jpg |

---

## 文件结构

```
album-tracker/
├── src/
│   ├── server.ts          # Express 服务器 + API 路由（双表同步逻辑）
│   ├── cli.ts             # CLI 工具
│   ├── db/database.ts     # 数据库连接层（sql.js）
│   └── types/album.ts     # TypeScript 类型定义
├── public/
│   ├── index.html         # 单页应用（Google Fonts 引入）
│   ├── css/style.css      # Editorial 风格样式
│   └── js/app.js          # 前端逻辑（双表同步调用）
├── covers/                # 专辑封面图片 ⭐
├── scripts/
│   ├── build.js           # esbuild 构建脚本
│   └── import_2026.py     # Markdown → SQLite 批量导入
├── dist/                  # 构建输出
├── docs/
│   └── 研发计划.md         # 详细开发计划
├── package.json
└── tsconfig.json
```

---

## API 端点

| 端点 | 方法 | 说明 | 双表同步 |
|------|------|------|---------|
| `/api/stats` | GET | 仪表盘统计 | — |
| `/api/albums` | GET | 搜索/浏览专辑 | — |
| `/api/albums/:id` | GET | 专辑详情 | — |
| `/api/artist/:name` | GET | 艺术家专辑 | — |
| `/api/top` | GET | 排行榜 | — |
| `/api/genres` | GET | 风格分布 | — |
| `/api/countries` | GET | 国家分布 | — |
| `/api/albums` | POST | 新增专辑 | ✅ 年份表+总表 |
| `/api/albums/:id` | PUT | 更新专辑 | ✅ 双表同步 |
| `/api/albums/:id` | DELETE | 删除专辑 | ✅ 双表同步 |
| `/api/albums/:id/listen` | POST | 收听+1 | ✅ 年份表+总表 |
