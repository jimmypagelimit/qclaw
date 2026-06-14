# 三源合一规划 — Album Tracker × RYM × Pitchfork

> 创建日期：2026-06-14
> 更新时间：2026-06-14（加入 MusicBrainz 数据源）
> 状态：规划中

---

## 一、现状诊断

### 数据库现状（`_music_latest.db`，520 张专辑）

| 数据 | 覆盖率 | 存储方式 |
|------|--------|----------|
| RYM 评分 (rym_rating) | 103/520 (20%) | albums 表内列 |
| RYM URL (rym_url) | 101/520 (19%) | albums 表内列 |
| RYM 评价数 (rym_ratings_count) | 103/520 (20%) | albums 表内列 |
| Pitchfork 评分 (pitchfork_score) | 20/520 (4%) | albums 表内列 |
| Pitchfork URL (review_url) | 20/520 (4%) | albums 表内列 |
| 两者都有 | 14/520 (3%) | — |
| 两者都无 | 411/520 (79%) | — |

### 问题

1. **RYM/PF 数据直接塞在 albums 表里** — 违反范式，每加一个数据源就要加列
2. **缺失大量数据** — 79% 的专辑无任何外部评分
3. **三个项目各自为战** — album-tracker（本地库）、rym-expert（Charts/流派）、pitchfork-expert（乐评/评分）无统一桥接
4. **没有存储抓取元数据** — 何时抓的、数据来源页、原始 HTML 等

---

## 二、设计原则

1. **不动原表** — albums/artists/genres/styles/listen_history 结构不变
2. **卫星表扩展** — 新建关联表，通过 album_id 外键关联
3. **一源一表** — 每个数据源一张表，方便独立维护和扩展
4. **可追溯** — 记录抓取时间、来源 URL、原始数据

---

## 三、卫星表设计

### 表 1：`external_ratings`（外部评分表）

统一存储所有数据源的评分信息，一行 = 一张专辑 × 一个数据源。

```sql
CREATE TABLE external_ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    album_id INTEGER NOT NULL,           -- 关联 albums.album_id
    source TEXT NOT NULL,                -- 'rym' | 'pitchfork' | 'tnd' | 'nme' | 'allmusic' | 'bea' | 'acclaimedmusic'
    score REAL,                          -- 评分（原始分，如 RYM 3.82/5, PF 8.6/10）
    score_scale TEXT,                    -- 评分制：'out_of_5' | 'out_of_10' | 'out_of_100' | 'stars_5' | 'letter' | 'rank'
    ratings_count INTEGER,               -- 评价人数/投票数
    rank INTEGER,                        -- 榜单排名（如 BEA #1, AM #15）
    url TEXT,                            -- 来源页面 URL
    raw_data TEXT,                       -- 原始 JSON（备用，存完整抓取结果）
    fetched_at TEXT,                     -- 抓取时间 ISO8601
    updated_at TEXT,                     -- 最后更新时间
    UNIQUE(album_id, source)             -- 一张专辑一个来源只有一条
);
```

**示例数据：**

| album_id | source | score | score_scale | ratings_count | url |
|----------|--------|-------|-------------|---------------|-----|
| 323 | rym | 3.82 | out_of_5 | 22077 | https://rateyourmusic.com/... |
| 323 | pitchfork | 8.6 | out_of_10 | NULL | https://pitchfork.com/... |
| 323 | tnd | 8 | out_of_10 | NULL | https://theneedledrop.com/... |
| 323 | bea | 15 | rank | NULL | https://besteveralbums.com/... |

### 表 2：`external_metadata`（外部元数据表）

存储评分以外的补充信息（流派标签、发行信息、厂牌等）。

```sql
CREATE TABLE external_metadata (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    album_id INTEGER NOT NULL,
    source TEXT NOT NULL,                -- 'rym' | 'pitchfork' | 'allmusic' | 'discogs' | 'musicbrainz'
    field TEXT NOT NULL,                 -- 字段名：'genre' | 'style' | 'label' | 'country' | 'duration' | 'track_count' | 'release_mbid' | 'artist_mbid'
    value TEXT,                          -- 值
    source_url TEXT,                     -- 来源页
    fetched_at TEXT,
    UNIQUE(album_id, source, field)      -- 同一专辑同一来源同一字段只存一条
);
```

**示例数据：**

| album_id | source | field | value |
|----------|--------|-------|-------|
| 323 | rym | genre | Indie Rock |
| 323 | rym | style | Lo-Fi Indie |
| 323 | allmusic | label | Matador |
| 323 | allmusic | duration | 59:22 |

### 表 3a：`external_reviews`（乐评元数据表）

只存元数据，不存正文。正文在 `review_contents` 中。

```sql
CREATE TABLE external_reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    album_id INTEGER NOT NULL,
    source TEXT NOT NULL,                -- 'pitchfork' | 'stereogum' | 'nme' | 'tnd'
    review_url TEXT NOT NULL,
    author TEXT,                         -- 乐评作者
    published_at TEXT,                   -- 发表日期
    title TEXT,                          -- 乐评标题
    is_bnm INTEGER DEFAULT 0,           -- Best New Music / Editor's Choice
    fetched_at TEXT,
    UNIQUE(album_id, source)
);
```

### 表 3b：`review_contents`（乐评正文表，一对多）

一篇乐评可有多个语言版本的正文，每个版本独立记录。

```sql
CREATE TABLE review_contents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    review_id INTEGER NOT NULL,          -- 关联 external_reviews.id
    lang TEXT NOT NULL DEFAULT 'en',     -- 'en' | 'zh' | 'ja'
    body TEXT NOT NULL,                  -- Markdown 格式正文
    version INTEGER DEFAULT 1,           -- 翻译版本号（1=初稿, 2=校对后...）
    created_at TEXT,
    updated_at TEXT,
    UNIQUE(review_id, lang, version)     -- 同一乐评同语言同版本唯一
);
```

**示例：**

| review_id | lang | version | body |
|-----------|------|---------|------|
| 1 | en | 1 | # Twin Fantasy... (原文) |
| 1 | zh | 1 | # 双子幻想... (初译) |
| 1 | zh | 2 | # 双子幻想... (校对后) |

### 表 4：`external_charts`（榜单数据表）

存储 RYM Charts / BEA / Acclaimed Music 等榜单排名。

```sql
CREATE TABLE external_charts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    album_id INTEGER,                    -- 可为 NULL（榜单中不在库的专辑）
    album_name TEXT,                     -- 冗余存，方便查不在库的
    artist TEXT,
    source TEXT NOT NULL,                -- 'rym' | 'bea' | 'acclaimedmusic' | 'nme'
    chart_type TEXT NOT NULL,            -- 'all_time' | 'decade_2020s' | 'year_2024' | 'genre_rock'
    rank INTEGER NOT NULL,
    score REAL,                          -- 榜单分数（如 BEA Rank Score）
    url TEXT,
    fetched_at TEXT,
    UNIQUE(source, chart_type, rank)     -- 同一榜单同一排名只存一条
);
```

---

## 四、迁移计划

### Phase 0：建表 + 数据迁移（不影响原表）

1. 创建 4 张卫星表
2. 将 albums 表中已有的 RYM 数据迁移到 `external_ratings`
3. 将 albums 表中已有的 PF 数据迁移到 `external_ratings`
4. **保留 albums 表的 rym_* / pitchfork_* 列**（向后兼容，暂不删除）
5. Web 服务查询改为优先读 `external_ratings`，fallback 读旧列

### Phase 1：批量数据回填

| 优先级 | 数据源 | 目标 | 预计覆盖 |
|--------|--------|------|----------|
| P0 | RYM | 520 张专辑评分补全 | 103→400+ |
| P1 | Pitchfork | 520 张专辑评分补全 | 20→150+ |
| P2 | TND (Fantano) | 评分抓取 | 0→80+ |
| P3 | AllMusic | 5星评分 + 元数据 | 0→200+ |
| P4 | BEA | 聚合排名 | 0→100+ |
| P5 | MusicBrainz | MBID + 年份确认 + 发行信息 | 0→300+ |

### Phase 2：深度数据

- Pitchfork 乐评正文 + 翻译 → `external_reviews`
- RYM 流派/风格标签 → `external_metadata`
- Charts 榜单数据 → `external_charts`
- Stereogum 月度栏目推荐 → `external_metadata`

### Phase 3：旧列清理

- 确认 Web 服务完全切到 `external_ratings` 后
- 删除 albums 表的 `rym_rating` / `rym_ratings_count` / `rym_url` / `pitchfork_score` / `review_url` 列
- 删除旧年度表（albums_2024/2025/2026）

---

## 五、统一查询视图

```sql
-- 评分总览视图：一张专辑所有来源的评分一行展示
CREATE VIEW v_album_ratings AS
SELECT
    a.album_id, a.album_name, a.artist, a.release_year,
    MAX(CASE WHEN er.source='rym' THEN er.score END) AS rym_score,
    MAX(CASE WHEN er.source='rym' THEN er.ratings_count END) AS rym_count,
    MAX(CASE WHEN er.source='pitchfork' THEN er.score END) AS pf_score,
    MAX(CASE WHEN er.source='tnd' THEN er.score END) AS tnd_score,
    MAX(CASE WHEN er.source='allmusic' THEN er.score END) AS am_score,
    MAX(CASE WHEN er.source='bea' THEN er.rank END) AS bea_rank,
    -- 标准化评分（统一为百分制）
    MAX(CASE WHEN er.source='rym' THEN er.score * 20 END) AS rym_pct,
    MAX(CASE WHEN er.source='pitchfork' THEN er.score * 10 END) AS pf_pct,
    MAX(CASE WHEN er.source='tnd' THEN er.score * 10 END) AS tnd_pct,
    MAX(CASE WHEN er.source='allmusic' THEN er.score * 20 END) AS am_pct
FROM albums a
LEFT JOIN external_ratings er ON a.album_id = er.album_id
GROUP BY a.album_id;

-- 评分分歧视图：找出不同来源评分差异大的专辑
CREATE VIEW v_rating_conflicts AS
SELECT
    a.album_name, a.artist,
    MAX(CASE WHEN er.source='rym' THEN er.score END) AS rym,
    MAX(CASE WHEN er.source='pitchfork' THEN er.score END) AS pf,
    MAX(CASE WHEN er.source='tnd' THEN er.score END) AS tnd
FROM albums a
JOIN external_ratings er ON a.album_id = er.album_id
WHERE a.album_id IN (
    SELECT album_id FROM external_ratings
    GROUP BY album_id HAVING COUNT(DISTINCT source) >= 2
)
GROUP BY a.album_id;
```

---

## 六、Web 服务改造

### API 新增端点

| 端点 | 功能 |
|------|------|
| `GET /api/albums/:id/ratings` | 获取某专辑所有来源评分 |
| `GET /api/albums/:id/reviews` | 获取某专辑所有乐评 |
| `GET /api/ratings/compare` | 评分对比（RYM vs PF vs TND） |
| `GET /api/charts/:source/:type` | 榜单数据查询 |

### 现有端点改造

- `/api/albums` — 返回中增加 `ratings` 子对象，包含所有来源评分
- `/api/albums?sort=rym` — 按 RYM 评分排序
- `/api/albums?sort=pf` — 按 PF 评分排序
- `/api/albums?sort=avg_rating` — 按标准化均分排序

---

## 七、执行路径

```
Phase 0 (建表+迁移)     → 不影响现有功能，可立即开始
    ↓
Phase 1 (批量回填)      → RYM 优先，已有 rym_tool.py
    ↓
Phase 2 (深度数据)      → PF 乐评、Charts、元数据
    ↓
Phase 3 (旧列清理)      → 最后一步，确认无依赖后执行
```

**Phase 0 估计时间：30 分钟**（建表 + 迁移 + 视图 + 验证）
**Phase 1 估计时间：数天**（分批抓取，RYM 每张 ~60s）

---

## 八、风险与对策

| 风险 | 对策 |
|------|------|
| RYM CF 拦截 | CloakBrowser + JS location.href 已验证可行 |
| PF 全 JS 渲染 | `__PRELOADED_STATE__` + web_fetch 已验证 |
| MusicBrainz SSL 错误 | 仅用搜索 API（`/ws/2/release/`），Cover Art / Genre Tags 走不通 |
| 数据不一致（同一专辑不同来源信息冲突） | 以本地库为主，外部数据仅供参考 |
| 卫星表 JOIN 性能 | SQLite 对小数据集（<10K）性能无忧 |
| Web 服务改造范围大 | Phase 0 不改 Web，仅建表迁移 |

---

## 九、MusicBrainz 数据源说明（2026-06-14）

### 接口可用性（实测）

| 接口 | 状态 | 用途 |
|------|------|------|
| `/ws/2/release/` 搜索 | ✅ Python 可通 | 查 MBID、年份、发行版本 |
| `/ws/2/artist/` 搜索 | ✅ Python 可通 | 查艺人 MBID、国家 |
| `/ws/2/release-group/{mbid}?inc=genres` | ❌ SSL 握手失败 | Genre tags 获取失败 |
| `coverartarchive.org` 封面 | ❌ SSL 握手失败 | 封面下载失败 |

### 原因分析
Python 3.11 urllib/requests 在 Windows 上 TLS 1.3 握手时，对 musicbrainz.org 部分后端节点（coverartarchive.org、所有 `/release-group/` 请求）报 `UNEXPECTED_EOF_WHILE_READING`。curl 可通，说明服务器正常，是 Python SSL 栈兼容性问题。

### 可用场景
- **MBID 获取**：搜索专辑/艺人得到 MusicBrainz ID，后续可用于精确查询
- **年份/发行信息确认**：RYM 搜索结果的 `date` 字段
- **中转站**：MBID → Discogs/其他支持 MBID 查询的 API

### User-Agent 要求
所有请求必须带 `User-Agent`，格式：`App名/版本 (联系方式)`
```python
headers={'User-Agent': 'AlbumTracker/1.0 (jim@example.com)'}
```

### 限速
1 req/sec，超速会 503。

---

_创建日期：2026-06-14_
_作者：小飞_
