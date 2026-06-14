# L 项目规划 — Lyrics Expert

> 创建日期：2026-06-15
> 状态：管道已验证，歌词源调研完成
> 负责人：小飞

---

## 一、项目目标

为 `album-tracker` 数据库中的专辑 **自动获取歌词**，存储为本地文件，支持：
- 英文歌词（含 LRC 时间戳）
- 中文歌词（含翻译）
- 双语对照（中英文并列）

---

## 二、歌词源调研结果（2026-06-15 实测）

### Tier 1：可直接使用 ✅

| 数据源 | 英文歌词 | 中文歌词 | 时间戳(LRC) | 翻译歌词 | API | 免费 | 备注 |
|--------|---------|---------|------------|---------|-----|------|------|
| **LRCLIB** | ✅ 100%命中率 | ❌ 无 | ✅ syncedLyrics | ❌ | REST API | ✅ | 英文首选，无需key |
| **网易云音乐** | ✅ 有 | ✅ 有 | ✅ LRC格式 | ✅ 中文翻译+时间戳 | HTTP API | ✅ | **中文首选**，需Referer头，搜索+歌词双API |

### LRCLIB API
```
GET https://lrclib.net/api/search?q=艺术家+歌曲
GET https://lrclib.net/api/get/{id}
```
- 无需 API Key，返回 JSON
- `syncedLyrics`（LRC 格式）+ `plainLyrics`
- 英文歌命中率接近100%
- **中文歌库为空**（刺猬乐队搜0结果）

### 网易云音乐 API（中文歌词核心源）
```
搜索: GET https://music.163.com/api/search/get?s=关键词&type=1&limit=10
歌词: GET https://music.163.com/api/song/lyric?id={song_id}&lv=1&tv=1
```
- **必须加 `Referer: https://music.163.com`**
- 返回 JSON，含 `lrc.lyric`（原歌词）+ `tlyric.lyric`（翻译歌词）
- **翻译歌词带时间戳**，可与原歌词逐行对齐
- 实测：Car Seat Headrest - Fill In The Blank，原歌词2361字+中文翻译947字，均有时间戳
- 翻译质量不错（非机器翻译，有人工审核）
- **已知限制**：搜索结果可能不精确（刺猬乐队搜出日文歌）；部分专辑需手机绑定（-462错误）

### Tier 2：可爬取但需处理 ⚠️

| 数据源 | 状态 | 英文 | 中文 | 翻译 | 获取方式 | 备注 |
|--------|------|------|------|------|---------|------|
| **LyricsTranslate** | ✅ 可爬 | ✅ | ✅ 多语种 | ✅ 人类翻译 | web_fetch | 艺人页面200OK，歌词在`<div class="ltf">`里，搜索页超时 |
| **Genius** | ❌ CF拦截 | ✅ | ❌ | ✅ annotation | 需CDP/Playwright | 403/404，CF保护；有API需access_token |
| **Musixmatch** | ❌ 403 | ✅ | ✅ | ✅ synced | 需API key | 商用收费，web_fetch 403 |
| **Bandcamp** | ⚠️ 手动 | 部分 | ❌ | ❌ | web_fetch逐页 | 部分独立专辑在描述里含歌词 |

### Tier 3：不可用 ❌

| 数据源 | 原因 |
|--------|------|
| AZLyrics | 404/超时 |
| Lyrics.com | 200OK但内容质量低 |
| ChartLyrics | 404 |
| OVH Lyrics API | 超时 |
| DarkLyrics | fetch失败 |
| Metal-Archives歌词 | CF保护(403) |

---

## 三、最终歌词获取策略

### 英文歌词管道
```
LRCLIB API → 逐首搜索 → 获取 syncedLyrics + plainLyrics → 保存
命中率: ~100%（英文专辑）
```

### 中文歌词+翻译管道
```
网易云音乐 API → 搜索歌名 → 获取song_id → 歌词API → 原歌词+翻译歌词 → 保存
命中率: 待批量验证
```

### 补充管道（冷门/小众专辑）
```
LyricsTranslate → web_fetch艺人页 → 提取歌曲链接 → 爬歌词页 → 解析<div class="ltf"> → 保存
命中率: 待验证
```

### 双语对齐方法
```
网易云原歌词(LRC) + 翻译歌词(LRC) → 按时间戳逐行对齐 → 生成双语对照文件
```

---

## 四、存储方案

### 目录结构
```
lyrics/
  {Artist}/
    {Album}/
      {Track}.lrc          # LRC 时间戳歌词（原语言）
      {Track}.txt          # 纯文本歌词（原语言）
      {Track}_zh.lrc       # 中文翻译歌词（LRC时间戳）
      {Track}_zh.txt       # 中文翻译歌词（纯文本）
      {Track}_bilingual.txt # 双语对照（中英逐行对齐）
```

### 与 album-tracker 集成
```sql
ALTER TABLE albums ADD COLUMN lyrics_status TEXT DEFAULT 'none';
-- none | partial | complete
ALTER TABLE albums ADD COLUMN netease_song_ids TEXT; -- JSON数组，存网易云曲目ID映射
```

不存歌词内容，只存状态 + 文件路径。

---

## 五、曲目获取方案

### MusicBrainz Playwright（已验证 ✅）
- 搜索 release-group → 选 Album → 打开 release → 提取曲目列表
- 已成功：Car Seat Headrest - Twin Fantasy (10首)
- **注意**：频繁请求会被限流(ERR_CONNECTION_CLOSED)，需等待冷却

### 网易云音乐曲目（中文歌备选）
- 搜索API返回曲目列表
- 可作为中文专辑的曲目来源

---

## 六、执行路径

```
Phase 0: 调研完成 ✅ → 今天已完成
Phase 1: LRCLIB批量管道 → 英文专辑歌词批量获取
Phase 2: 网易云批量管道 → 中文歌词+翻译批量获取
Phase 3: LyricsTranslate补充 → 冷门专辑翻译歌词
Phase 4: 双语对齐工具 → 自动生成中英对照文件
Phase 5: Web界面集成 → album-tracker歌词Tab
```

---

## 七、项目文件清单

```
tasks/lyrics-expert/
  PLAN.md                    # 本文档
  lyrics_pipeline.py         # 完整管道（MB曲目→LRCLIB歌词）
  mb_playwright.py           # MB曲目提取（Playwright）
  mb_tracklist.py            # 独立曲目提取脚本
  reports/                   # 调研报告
    lyrics_sources_survey.json   # 初步调研结果
    deep_survey_results.json     # 深度调研结果
    deep_survey_log.txt          # 深度调研日志
    netease_translated_sample.lrc # 网易云翻译歌词样本
  lyrics/                    # 歌词文件存储
    Car Seat Headrest Twin Fantasy/  # 已验证专辑
      *.lrc, *.txt
  tracklists/                # 曲目列表JSON
```

---

_创建日期：2026-06-15_
_更新日期：2026-06-15（调研完成，PLAN重写）_
_作者：小飞_