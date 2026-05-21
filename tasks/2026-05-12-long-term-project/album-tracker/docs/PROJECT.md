# 专辑收听次数维护展示系统 - 项目文档

**创建时间：** 2026-05-12
**版本：** v1.0 (功能上线，封面系统完成)
**维护者：** 小飞 (XiaoFei)

---

## 一、项目概述

构建一个用于**维护**和**展示**专辑收听次数的系统，核心能力是：
1. 记录每次收听行为（时间、专辑、次数）
2. 补充专辑元数据（封面图、风格、发行年份、艺术家等）
3. 多维度展示（统计图表、专辑库浏览、详情查看）

---

## 二、数据库

### 2.1 位置与规模
```
G:\原创计划\music
```
- 格式：SQLite（无扩展名）
- 截至 2026-05-14：

| 表名 | 记录数 | 说明 |
|------|--------|------|
| albums | 497 | 主表（所有专辑） |
| albums_2024 | ~240 | 2024 年开始听的专辑 |
| albums_2025 | ~190 | 2025 年开始听的专辑 |
| albums_2026 | ~180 | 2026 年开始听的专辑 |

### 2.2 表结构（4 表 schema 完全一致）

```sql
CREATE TABLE albums (
    album_id INTEGER PRIMARY KEY AUTOINCREMENT,
    album_name TEXT NOT NULL,              -- 专辑名
    artist TEXT NOT NULL,                  -- 艺术家
    country TEXT,                          -- 国家
    region TEXT,                           -- 地区
    genre TEXT,                            -- 风格标签
    rating REAL,                           -- 评分
    description TEXT,                      -- 描述
    is_compilation INTEGER DEFAULT 0,      -- 是否合辑
    first_listen_date TEXT,                -- 首次收听日期
    total_listen_count INTEGER DEFAULT 1,  -- 总收听次数
    release_company TEXT,                  -- 发行公司
    cover_image_url TEXT,                  -- 封面图 URL（指向 /covers/{id}-COV.jpg）
    duration TEXT,                         -- 时长
    composition_score REAL,                -- 作曲评分
    lyrics_meaning_score REAL,             -- 歌词意境评分
    creativity_score REAL,                 -- 创意评分
    arrangement_score REAL,                 -- 编曲评分
    vocal_performance_score REAL,          -- 演唱评分
    instrumental_performance_score REAL,   -- 器乐演奏评分
    sincerity_score REAL,                 -- 真诚度评分
    subjective_score REAL,                -- 主观评分
    overall_score REAL,                   -- 综合评分
    release_year TEXT,                    -- 发行年份
    style TEXT,                           -- 风格细分
    producer TEXT                          -- 制作人
);
```

### 2.3 双表同步机制（核心设计）

- **写操作同时写入** `albums` 总表 + 对应年份表（albums_2024/2025/2026）
- 关联依据：`album_name + artist`
- **albums 表 ID** 与年份表 ID **独立**，不得混淆
- albums 表的 `cover_image_url` 指向 `/covers/{albums.album_id}-COV.jpg`
- 年份表（如 albums_2026）的 `cover_image_url` 同样指向总表 ID 对应的封面文件

### 2.4 数据质量（截至 2026-05-14）

| 指标 | 状态 | 说明 |
|------|------|------|
| 封面图 | ✅ **100% 完成** | albums 497 张全有，albums_2026 收听专辑 123 张全有 |
| 风格标签 | 部分有 | 主流专辑有，中文独立/地下缺失 |
| 评分字段 | 部分有 | composition_score/overall_score 等有值 |
| 收听次数 | ✅ 有值 | |

---

## 三、封面系统 ⭐ 已完成

### 3.1 覆盖规模
- albums 表：497/497 有封面（100%）
- albums_2026 有收听记录专辑：123/123 有封面（100%）

### 3.2 封面来源优先级
1. **iTunes**（主力，质量高）
2. **Deezer**（备选）
3. **网易云音乐**（中文专辑）
4. **QQ 音乐**（补充）
5. **MusicBrainz Cover Art Archive**（备用）

### 3.3 封面文件命名
- 格式：`{albums.album_id}-COV.{ext}`
- 路径：`album-tracker/covers/`
- 示例：`178-COV.jpg`、`447-COV.jpg`
- **命名依据是 albums 表的真实 ID，不是顺序号，不是年份表 ID**

### 3.4 下载工具
```bash
# 单次下载
cd tasks/album-tracker
node dist/download-covers.js --count 10

# 批量脚本（手动写 Python）
python download_covers_batch.py
```

> ⚠️ 注意：sql.js 把整个 DB 加载到内存，封面下载后需重启服务器才能在 Web UI 看到

---

## 四、功能模块

### 4.1 CLI 工具（已完成）

入口：`node dist/cli.js <command>`

| 命令 | 说明 |
|------|------|
| `search <关键词>` | 搜索专辑，支持 album_name/artist/year/score |
| `info [-i ID] [关键词]` | 查看专辑详情，-i 优先从年份表查询 |
| `stats` | 全局统计：专辑总数、年份分布、国家分布 |
| `top [数量]` | 显示收听次数最多的专辑 |
| `add <album> <artist>` | 添加新专辑到 albums 表 |
| `edit <id> <field> <value>` | 编辑专辑字段 |
| `delete [-i ID] [关键词]` | 删除专辑 |
| `listen [-i ID] [关键词]` [-c N] | 收听 +1，支持 -t 指定年份表 |
| `import [--all]` | 导入历史数据（支持华语/外语 + 新歌/老歌分类）|

**关键行为：**
- `-i ID` 自动优先从年份表查询（albums_2026 > albums_2025 > albums_2024 > albums）
- `search` 默认从总表输出，支持 `-t <表名>` 指定年份表
- 所有写操作后需手动重启服务器：`node dist/server.js`

### 4.2 Web UI（已完成）

访问：http://localhost:3456（纯展示，无维护功能）

**页面：**
- **仪表盘**：统计卡片 + 收听趋势柱状图 + 年度 Top 3 对比图
- **专辑库**：卡片网格 + 搜索框 + 排序（评分/收听/名称/艺术家/年份）

**API 端点：**
| 端点 | 说明 |
|------|------|
| `GET /api/albums` | 专辑列表，支持 `sort` / `dir` / `year` / `q` 参数 |
| `GET /api/albums/:id` | 专辑详情 |
| `GET /api/stats` | 全局统计 |
| `GET /api/top-by-year` | 每年 Top 3 专辑 |
| `GET /api/years` | 年份列表 |

### 4.3 维护流程

**添加/修改收听后：**
1. CLI 写入数据库（磁盘）
2. 重启 Web 服务器：`node dist/server.js`（sql.js 需重新加载 DB）

**每日封面补全（HEARTBEAT）：**
1. 停 Web 服务器
2. `node dist/download-covers.js --count 10`
3. 重启 Web 服务器
4. 飞书通知结果

---

## 五、技术栈

- **语言：** TypeScript
- **运行时：** Node.js
- **数据库：** SQLite（`G:\原创计划\music`）
- **DB 访问：** sql.js（内存模型）+ sqlite3 CLI（MSYS2，直接磁盘访问）
- **CLI：** Commander.js
- **Web 框架：** Express.js + TypeScript
- **前端：** Vanilla JS + ECharts
- **构建：** esbuild（src → dist）
- **音频封面提取：** ffmpeg

### 目录结构
```
album-tracker/
├── dist/
│   ├── cli.js           # CLI 入口
│   ├── server.js        # Web 服务器入口
│   └── download-covers.js  # 封面下载工具
├── public/
│   ├── index.html
│   ├── detail.html
│   └── js/app.js        # 前端 JS
├── src/
│   ├── cli.ts
│   ├── server.ts
│   └── download-covers.ts
├── covers/              # 封面文件存储
│   └── {album_id}-COV.{ext}
├── scripts/             # 数据导入脚本
│   └── import_2026.py
├── docs/
│   ├── PROJECT.md       # 本文档
│   └── 研发计划.md
└── start_server.bat     # 服务器启动脚本
```

---

## 六、已知问题与待做

### 已知问题

| 优先级 | 问题 | 状态 |
|--------|------|------|
| P2 | P2-7 专辑详情弹窗增强（封面放大/歌词/乐评入口） | ❌ 未做 |
| P2 | searchAlbums() 后端排序完整性待验证 | ❌ 待确认 |
| P3 | 中文独立/地下乐队封面缺失（主流 API 无索引） | 需手动补充 |
| P3 | CLI `restart_server` 自动重启功能未实现 | ❌ 未做 |

### 下一步计划

- **P2-7**（45min）：专辑详情弹窗增强
- **P3**：CLI 交互模式 / 数据导入导出 / 自动重启
- **长期**：封面覆盖率 100%（497→更多专辑）

---

## 七、数据库字段说明

### 评分体系（10 分制）

| 字段 | 含义 |
|------|------|
| composition_score | 作曲 |
| lyrics_meaning_score | 歌词意境 |
| creativity_score | 创意 |
| arrangement_score | 编曲 |
| vocal_performance_score | 演唱 |
| instrumental_performance_score | 器乐演奏 |
| sincerity_score | 真诚度 |
| subjective_score | 主观评分 |
| overall_score | 综合评分 |

### 风格标签（genre / style）

- Indie Rock / Noise Rock / Post-Punk / Shoegaze / Metal / Hardcore Punk
- Indie Folk / Folk Rock / Country Folk
- Mandopop / C-Pop / Taiwan Indie
- Jazz / Fusion / Free Jazz
- 等

---

**文档更新日志：**
- 2026-05-12 v0.1：创建项目文档，需求分析
- 2026-05-12 v0.2：数据库分析完成，封面系统规划
- 2026-05-14 v1.0：CLI + Web UI 上线，封面系统 100% 完成