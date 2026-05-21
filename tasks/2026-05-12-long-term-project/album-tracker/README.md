# 专辑数据库管理工具

专辑收听次数维护展示系统，提供 **CLI 工具** + **Web 界面**。

## 快速开始

### 1. 安装依赖

```bash
cd album-tracker
npm install
```

### 2. 构建

```bash
npm run build
```

### 3. 启动 Web 服务器

```bash
node dist/server.js
```

浏览器访问 **http://localhost:3456**

默认端口 3456，可自定义：
```bash
PORT=8080 node dist/server.js
```

### 4. 使用 CLI 工具

```bash
# 搜索专辑
node dist/cli.js search 海龟
node dist/cli.js search "Car Seat Headrest" --limit 20

# 查看专辑详情
node dist/cli.js info --id 1 --table albums

# 查看艺术家专辑
node dist/cli.js artist --name "刺猬乐队"

# 添加专辑
node dist/cli.js add --name "新专辑" --artist "艺术家" --genre "Indie Rock" --year 2025

# 编辑专辑
node dist/cli.js edit --id 123 --rating 8.5 --genre "Post-Punk"

# 删除专辑
node dist/cli.js delete --id 123 --yes

# 记录收听
node dist/cli.js listen --id 123 --count 1

# 统计总览
node dist/cli.js stats

# 收听排行榜
node dist/cli.js top --limit 20
```

## Web 界面功能

| 页面 | 功能 |
|------|------|
| **仪表盘** | 统计卡片 + 风格/国家分布图表 |
| **专辑库** | 搜索、分页浏览、快速收听+1 |
| **排行榜** | 总排行/年度排行、Top 10/20/50 |
| **新增专辑** | 完整表单（含入库名份选择） |

## 核心逻辑：双表同步 ⭐

所有写操作（新增/收听/编辑/删除）**同时操作年份表和总表**。

### 数据库结构

| 表 | 含义 |
|---|---|
| `albums` | 总库（所有年份汇总） |
| `albums_2024` | 2024年入库/收听的专辑 |
| `albums_2025` | 2025年入库/收听的专辑 |
| `albums_2026` | 2026年入库/收听的专辑 |

### 同步规则

- **新增专辑** → 写入年份表 + 写入总表（已存在则 +1）
- **收听 +1** → 更新年份表 + 更新总表（年份表无则新增）
- **编辑专辑** → 双表同步更新
- **删除专辑** → 双表同步删除
- **跨表关联**：`album_name + artist`（album_id 各表独立）

### 统计规则

| 查询 | 查哪张表 |
|------|---------|
| 总排行 | `albums` |
| 年度排行 | `albums_YYYY` |

## CLI 命令参考

| 命令 | 说明 |
|------|------|
| `search [keyword]` | 搜索专辑 |
| `info -i <id>` | 查看专辑详情 |
| `artist -n <name>` | 查看艺术家专辑 |
| `add -n <name> -a <artist>` | 添加专辑 |
| `edit -i <id>` | 编辑专辑 |
| `delete -i <id>` | 删除专辑 |
| `listen -i <id>` | 记录收听 |
| `stats` | 统计总览 |
| `top` | 排行榜 |

## 数据库

- **路径**: `G:\原创计划\music`
- **格式**: SQLite（无扩展名）
- **表**: `albums` (389条), `albums_2024` (243条), `albums_2025` (192条), `albums_2026`
- **字段**: 25 个（详见 PROJECT.md）

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Express.js + TypeScript |
| 数据库 | sql.js（纯 JS SQLite） |
| 前端 | 原生 HTML/CSS/JS |
| 构建 | esbuild |
| 风格 | Editorial/Magazine（详见 PROJECT.md） |

## 更多文档

- [PROJECT.md](./PROJECT.md) - 完整项目文档（双表同步逻辑 + UI 风格指南）
- [docs/研发计划.md](./docs/研发计划.md) - 详细开发计划
