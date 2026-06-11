# RYM Rock 风格树建立（2026-06-10）

## 目标
把 RYM 的 81 个 Rock 子流派写入数据库 styles 表，建立树形层级（parent_id），并同步 album_styles junction 表。

## 执行过程

### 1. 数据库 schema 变更
ALTER TABLE styles 新增三列：
- `rym_slug TEXT` — RYM URL slug（如 `krautrock`）
- `parent_id INTEGER DEFAULT 0` — 父节点（Rock = 1）
- `category TEXT` — 视觉组织分类

### 2. 插入 81 个 RYM Rock 子流派
从 RYM `/genre/rock/` 页面抓取的 81 个子流派，按音乐学脉络归为 9 大类：
- **Rock & Roll / Early Rock** (3): Rock & Roll, Rockabilly, Surf Rock
- **Garage / Punk** (5): Garage Rock, Garage Rock Revival, Punk Rock, Frat Rock, Crack Rock Steady
- **Indie / Alternative** (16): Alternative Rock, Indie Rock, Noise Rock, Post-Rock, Slacker Rock, Post-Punk, Noise Pop, Blackgaze, Slowcore, Lo-Fi, Dream Pop, Shoegaze, Emo, Chinese Indie
- **Folk Rock** (10): Folk Rock, Indie Folk, Psychedelic Folk, Americana, Celtic Rock 等
- **Psychedelic / Progressive / Art** (16): Psychedelic Rock, Progressive Rock, Krautrock, Math Rock, Space Rock, Art Rock, Experimental Rock 等
- **Hard / Heavy** (12): Hard Rock, Stoner Rock, Blues Rock, Southern Rock, Gothic Rock, Deathrock, Classic Rock 等
- **Glam / Pop / Soft** (13): Pop Rock, Soft Rock, Glam Rock, Country Rock, Jazz-Rock, Funk Rock, Yacht Rock, Piano Rock 等
- **Industrial / Electronic** (3): Industrial Rock, Machine Rock, Beat Rock
- **Regional / World Rock** (20): Afro-Rock, Anatolian Rock, Chinese Rock, Taiwanese Rock, Zamrock, Deutschrock 等

### 3. 关联原有 18 个已存在的 Rock 风格
将原 styles 表中已有的 Rock 相关风格（Garage Rock, Art Rock, Experimental Rock, Pop Rock, Alternative Rock, Indie Rock, Folk Rock, Post-Rock, Post-Punk 等）标记 parent_id=1，形成统一树。

### 4. 清理脏数据
删除 13 条描述性文字混入风格名的脏记录（style_id 77-78, 83, 86-96）。

### 5. 同步 album_styles junction 表
将 `albums.style` 文本字段映射到 styles.style_id，补充 36 条 junction 记录：
- Psychedelic Rock, Hard Rock, Classic Rock, Prog Rock, Chinese Rock, Taiwanese Rock, Noise, Shoegaze, Dream Pop, Lo-Fi, Emo 等

## 最终数据

- **styles 表**: 162 条（97→162）
- **Rock 子流派**: 98 个（parent_id=1）
- **album_styles**: ~528 条（492→528）
- **API 验证**: `/api/styles` 返回 Rock 152张、Pop 132张、Metal 57张

## Git 提交
- commit: `acf7571`
- 内容: `_music_latest.db` + `rym-rock-style-tree.json`
- 知识库文件: `album-tracker/data/rym-rock-style-tree.json`

## API 端点
- `GET /api/styles?limit=20` — Top 20 风格分布（基于 junction 表）
- `GET /api/stats` — 含 genres + styles 分布统计
- `GET /api/albums?genre=Rock` — 按风格筛选专辑