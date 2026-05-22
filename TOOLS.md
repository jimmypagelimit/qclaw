# TOOLS.md - Local Notes

## 命令执行优先级（永久规则）

**Python 永远是绝对第一选择** ✅

1. **Python** — `C:\Python311\python.exe`（绝对第一，所有任务优先用 Python）
2. **Node.js** — `node`（仅当 Python 不合适时用，如 album-tracker CLI）
3. **CMD** — `cmd /c`（仅简单命令，Python 无法处理时）
4. **Git Bash** — `C:\Progra~1\Git\bin\bash.exe -l`（仅 Git 操作）
5. ~~PowerShell~~ ❌ **永久禁用，永远别用**

### 铁律
- 所有脚本、API 调用、数据处理 → **必须用 Python**
- 只有 Python 明显不合适时才考虑 Node.js/CMD
- PowerShell 永远不用，没有例外

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

### Python 调 API 示例
```python
import urllib.request, json

# GET 示例
url = "http://localhost:3456/api/stats"
data = json.loads(urllib.request.urlopen(url).read())
print(data)

# POST 示例
req = urllib.request.Request(
    "http://localhost:3456/api/albums",
    data=json.dumps({"album_name": "xxx", "artist": "xxx"}).encode(),
    headers={"Content-Type": "application/json"}
)
resp = json.loads(urllib.request.urlopen(req).read())
```

## 文件搜索

**使用 Everything HTTP 服务进行本地文件搜索**

**Python 调用：**
```python
import urllib.request
resp = urllib.request.urlopen("http://localhost:18000/?search=关键词").read()
print(resp.decode())
```

**或用 CMD 的 curl：**
```cmd
curl "http://localhost:18000/?search=关键词"
```

## ffmpeg

- **路径**: `C:\ffmpeg\ffmpeg.exe`
- **版本**: 8.1.1 (essentials)

```bash
C:\ffmpeg\ffmpeg.exe -i input.mp3 output.wav
```

## OpenCLI Chrome 扩展（已配置）⭐
- **版本**: v1.8.0
- **功能**: 查 B 站热榜等
- **配置**: Chrome/Edge 开发者模式 → 加载已解压的扩展
- **启动**: `opencli daemon restart`

## opencli + CDP 浏览器自动化 ✅ **首选方案**

### 背景
QEMU 虚拟机中所有自行启动浏览器的方案都被 SIGKILL 杀死。
解决思路：**不启动浏览器，连接到已有的 Chrome**。

### 启动 Chrome（手动，CMD 命令）
```cmd
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --no-sandbox --remote-debugging-port=9222 --remote-allow-origins=*
```

### 关键参数
- `--no-sandbox` → QEMU 虚拟机中必须
- `--remote-debugging-port=9222` → 开启 CDP
- `--remote-allow-origins=*` → 允许 WebSocket 连接

### opencli 命令
```bash
opencli browser work bind          # 绑定到现有 Chrome
opencli browser work open <url>    # 打开 URL
opencli browser work screenshot    # 截图
opencli browser work state         # 查看页面元素
opencli browser work click <n>     # 点击元素
opencli browser work type <n> <text>  # 输入
opencli browser work extract       # 提取内容为 markdown
opencli browser work close         # 释放会话
```

### 注意事项
- 143 个站点有专属适配器（Google、B站、GitHub 等）
- 保持 Chrome 登录态，cookie/会话都在
- CDP 9222 仅本地监听，安全

## 网页抓取注意事项

### RSS 抓取（独立音乐动态）
- Pitchfork RSS: `https://pitchfork.com/feed/rss` ✅ 稳定
- Stereogum RSS: `https://www.stereogum.com/feed/` ✅ 稳定
- Metal Injection RSS: `https://metalinjection.net/feed/` ✅ 稳定
- UPEE: `https://upee.substack.com/feed` ✅ 稳定
- BrooklynVegan/NME/Consequence RSS 时有 404
- The Quietus/RYM/Metacritic 有 CF 保护，`web_fetch` 返回 403

### 浏览器自动化
**使用 opencli + CDP 方案**（见上方），不需要单独安装 Chrome。
Cloudflare 拦截时优先用此方案。

### Cloudflare 拦截
- `web_fetch` 被强 CF 站（RYM、The Quietus、Slant、BrooklynVegan）拦截是常态
- **优先用 opencli + CDP！**
- 替代数据源：AnyDecentMusic（`anydecentmusic.com`）无 CF，有加权评分

### 乐评汇编 Skill
- 位置：`{qclaw_skill_dir}/album-review-compiler/SKILL.md`
- 触发词：乐评、乐评翻译、album review
- 策略：Pitchfork 优先 → Stereogum → NME → 其他无 CF 源

## 外置硬盘状态
- G 盘（音乐编年史）、H 盘（荒岛唱片）均为外置硬盘
- 未挂载时本地只有 C 盘可用
- 搜索前先用 Everything HTTP 或 Python 确认磁盘在线

**Python 检查磁盘：**
```python
import os
print(os.path.exists("G:\\音乐编年史"))
```

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
- **注意**：需 opencli + CDP 绕过 Cloudflare

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

**Python 调用示例：**
```python
import urllib.request, json
url = "https://lrclib.net/api/search?q=Car+Seat+Headrest+Twin+Fantasy"
data = json.loads(urllib.request.urlopen(url).read())
print(data)
```

### lyricsgenius（Python 库）
- **安装**: `C:\Python311\Scripts\pip.exe install lyricsgenius`
- **需申请 Access Token**：`https://genius.com/api-clients`

### Lyricstranslate.com
- `web_fetch` 直接抓取，适合中文歌词翻译

### Bandcamp 专辑页
- 很多独立乐队把歌词放在专辑描述里

---

_Last updated: 2026-05-22_
