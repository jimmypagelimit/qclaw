# TOOLS.md - Local Notes

## 命令执行优先级

### 脚本/自动化
1. **Python** — `C:\Python311\python.exe`（主力，所有脚本优先用 Python）
2. **PowerShell** — 系统内置，.NET 能力
3. **Git Bash** — `C:\Program Files\Git\bin\bash.exe`（仅 Git 操作，有 credential helper）

### Git 操作（重要！）
**优先使用 Git Bash**，不用 PowerShell！

原因：Git Bash 有 credential helper，能访问 Windows 凭据管理器。

**用法：**
```bash
cmd /c "C:\Progra~1\Git\bin\bash.exe -l 脚本路径.sh"
```

## Python 环境

- **路径**: `C:\Python311\python.exe`
- **pip**: `C:\Python311\Scripts\pip.exe`
- **镜像源**: 阿里云 `https://mirrors.aliyun.com/pypi/simple/`
- **pip 配置**: `%APPDATA%\pip\pip.ini`

### 常用包安装
```bash
C:\Python311\Scripts\pip.exe install 包名
```

## 文件搜索

**使用 Everything HTTP 服务进行本地文件搜索**

```bash
curl.exe "http://localhost:18000/?search=关键词"
```

## ffmpeg

- **路径**: `C:\ffmpeg\ffmpeg.exe`
- **版本**: 8.1.1 (essentials)

```bash
C:\ffmpeg\ffmpeg.exe -i input.mp3 output.wav
```

## 网页抓取注意事项

### RSS 抓取（独立音乐动态）
- Pitchfork RSS: `https://pitchfork.com/feed/rss` ✅ 稳定
- Stereogum RSS: `https://www.stereogum.com/feed/` ✅ 稳定
- Metal Injection RSS: `https://metalinjection.net/feed/` ✅ 稳定
- UPEE: `https://upee.substack.com/feed` ✅ 稳定
- BrooklynVegan/NME/Consequence RSS 时有 404
- The Quietus/RYM/Metacritic 有 CF 保护，`web_fetch` 返回 403

### 浏览器自动化
**使用 OpenClaw 内置 browser 工具**（Chromium），不需要单独安装 Chrome。
Cloudflare 拦截时优先用 browser 工具。

### Cloudflare 拦截
- `web_fetch` 被强 CF 站（RYM、The Quietus、Slant、BrooklynVegan）拦截是常态
- **优先用 browser 工具！**
- 替代数据源：AnyDecentMusic（`anydecentmusic.com`）无 CF，有加权评分

### 乐评汇编 Skill
- 位置：`{qclaw_skill_dir}/album-review-compiler/SKILL.md`
- 触发词：乐评、乐评翻译、album review
- 策略：Pitchfork 优先 → Stereogum → NME → 其他无 CF 源

## 外置硬盘状态
- G 盘（音乐编年史）、H 盘（荒岛唱片）均为外置硬盘
- 未挂载时本地只有 C 盘可用
- 搜索前先用 Everything HTTP 或 `Get-PSDrive` 确认磁盘在线

## 音乐数据查询工具

### MusicBrainz（强烈推荐）⭐
- **网址**：https://musicbrainz.org
- **API**：`https://musicbrainz.org/ws/2/`

### Discogs
- **网址**：https://www.discogs.com
- **注意**：有 Cloudflare 保护

### Bandcamp
- **网址**：https://bandcamp.com
- **已验证可直接抓取**

### AnyDecentMusic
- **网址**：https://anydecentmusic.com
- **用途**：综合评分聚合，无 CF

### Metal-Archives
- **网址**：https://www.metal-archives.com
- **注意**：需 browser 工具绕过 Cloudflare

## 歌词获取工具

### 实测访问状态

| 站 | 地址 | 状态 | 说明 |
|---|---|---|---|
| Genius | genius.com | ❌ | Cloudflare 拦截 |
| AZLyrics | azlyrics.com | ❌ | 超时 |
| **Lyricstranslate** | lyricstranslate.com | ✅ | 免费，有翻译 |
| **LRCLIB** | lrclib.net | ✅ | 免费开源 REST API |

### LRCLIB（最推荐）⭐
- **API**: `GET https://lrclib.net/api/search?q=艺术家+歌曲`

### lyricsgenius（Python 库）
- **安装**: `C:\Python311\Scripts\pip.exe install lyricsgenius`
- **需申请 Access Token**：`https://genius.com/api-clients`

### Lyricstranslate.com
- `web_fetch` 直接抓取，适合中文歌词翻译

### Bandcamp 专辑页
- 很多独立乐队把歌词放在专辑描述里

---

_Last updated: 2026-05-22_
