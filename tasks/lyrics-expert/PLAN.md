# L 项目规划 — Lyrics Expert

> 创建日期：2026-06-15
> 状态：初始化中
> 负责人：小飞

---

## 一、项目目标

为 `album-tracker` 数据库中的专辑 **自动获取歌词**，存储为本地文件，支持：
- 中文歌词（含翻译）
- 英文歌词
- 双语对照（中英文并列）

---

## 二、数据源评估（基于已有经验）

| 数据源 | 状态 | 说明 |
|--------|------|------|
| **LRCLIB** | ✅ 英文首选 | 免费 REST API，返回 LRC 格式 ✅ 实测 English OK ❌ 中文无数据 |
| **Lyricstranslate** | ✅ 中文首选 | 免费，有翻译，需爬页面 |
| **Bandcamp** | ⚠️ 补充 | 部分独立专辑在专辑描述里含歌词，需逐页检查 |
| Genius | ❌ CF 拦截 | Cloudflare 保护，绕不过 |
| AZLyrics | ❌ 超时 | 连接不稳定 |

### LRCLIB API（最推荐）

```
GET https://lrclib.net/api/search?artist_name=Car+Seat+Headrest&track_name=Twin+Fantasy
GET https://lrclib.net/api/get/{id}
```

- 无需 API Key
- 返回 JSON，含 `syncedLyrics`（LRC 格式）和 `plainLyrics`
- 速率宽松，适合批量

### Lyricstranslate.com

- `web_fetch` 可直接抓页面
- 歌词在 `<div class="lyrics">` 里
- 有中文翻译

---

## 三、存储方案

### 方案 A：文件系统（推荐）
```
lyrics/
  {album_id}/
    {track_number:02d}_{track_name}.lrc   # 时间戳歌词
    {track_number:02d}_{track_name}.txt   # 纯文本
```

### 方案 B：数据库（不推荐）
- `lyrics` 表太大，且 SQLite 不适合存大文本
- 优先文件系统

---

## 四、与 album-tracker 集成

### 数据库改动（最小）
在 `albums` 表加一列：
```sql
ALTER TABLE albums ADD COLUMN lyrics_status TEXT DEFAULT 'none';
-- none | partial | complete
```

不存歌词内容，只存状态 + 文件路径。

### Web 界面
- 专辑详情页增加「歌词」Tab
- 点击曲目名，弹出歌词（LRC 可渲染为滚动歌词）

---

## 五、执行路径

```
Phase 0: 建项目目录 + 规划文档          → 今天
Phase 1: LRCLIB 脚本（按 album_id 批量） → 优先
Phase 2: Lyricstranslate 补充（中文）   → 冷门专辑
Phase 3: Bandcamp 补充（独立专辑）      → 手动指定
Phase 4: Web 界面集成                   → 最后
```

---

## 六、完整管道设计

### 管道：`lyrics_pipeline.py`
```
1. MusicBrainz 搜索 → 拿 release-group ID + release ID
   ↓
2. MusicBrainz lookup → 拿曲目列表（position + title + duration）
   ↓
3. 逐首曲目调 LRCLIB → 搜歌词 + 获取完整歌词
   ↓
4. 保存 .lrc + .txt 到 lyrics/{artist}/{album}/
   ↓
5. 保存曲目列表到 tracklists/{artist}-{album}.json
```

### 曲目信息来源：MusicBrainz
- **搜索 API** (`/ws/2/release-group/`)：拿 release-group ID
- **Lookup API** (`/ws/2/release/{id}?inc=recordings`)：拿曲目列表
- **Windows 稳定性**：间歇性不可用（SSL 问题），搜索偶尔能通，lookup 大概率挂
- **Fallback**：搜索和 lookup 都先 curl 后 Python urllib
- **离线模式**：可手动创建曲目列表 JSON 到 `tracklists/` 目录

### 歌词保存结构
```
lyrics/
  Car Seat Headrest/
    Twin Fantasy/
      My Boy.lrc      # LRC 时间戳歌词
      My Boy.txt      # 纯文本
      ...
tracklists/
  Car Seat Headrest-Twin Fantasy.json  # 曲目列表
```

---

## 七、待确认

1. **MusicBrainz 恢复后批量跑** — 当前 Windows 环境间歇性全挂
2. **歌词文件存储位置** — 当前在 `tasks/lyrics-expert/lyrics/`，后续可能移到 `album-tracker/public/lyrics/`
3. **优先级** — 先搞哪些专辑的歌词？
4. **中文歌词** — LRCLIB 无中文数据，需另建 Lyricstranslate 管道

---

_创建日期：2026-06-15_
_作者：小飞_
