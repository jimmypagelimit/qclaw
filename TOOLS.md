# TOOLS.md - Local Notes

## ⚠️ 听歌记录数据库路径（最高优先级，2026-06-12 确立）

**唯一正确的数据库路径**（Web 服务 `database.ts` 中 `DEFAULT_DB_PATH`）：
```
C:\Users\qujt\.qclaw\workspace\_music_latest.db
```

### 禁止使用的路径
- ❌ `album-tracker/_music_latest.db` — 是副本，可能过期
- ❌ `album-tracker/music.db` — 空文件
- ❌ `\\10.0.2.4\qemu\原创计划\music\music` — UNC 路径已废弃

### 操作规则（2026-07-14 重构）
**写操作：必须用 API，永远不 kill**
- POST /api/albums — 新增专辑+自动加listen（存在则只加listen）
- POST /api/albums/:id/listen — 追加收听次数
- PUT /api/albums/:id — 更新专辑信息
- sql.js 内存数据库，改完后需重启服务才能同步
- 首次写操作前 kill+重启一次，之后批量写不需要再 kill

**查操作：随意，直接读 DB 或 API 均可**

**禁止**：直接 sqlite3.connect() + kill 的旧流程

---

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

### ⚠️ GBK编码铁律（2026-06-10 事故后确立，永久生效）
- Windows 控制台 GBK 编码会导致中文乱码，**禁止用 print() 查看数据库中的中文**
- 查询中文数据**必须用 `repr(name)` 或写入文件查看**，否则乱码可能导致误删
- 删除任何记录前**必须用 repr() 确认中文内容**
- **PowerShell 永远不用，没有例外**
- Git 操作必须用 Git Bash（`cmd /c "C:\Progra~1\Git\bin\bash.exe -l ..."`）

### Git 操作（重要！）
**优先使用 Git Bash**，不用 PowerShell！

原因：Git Bash 有 credential helper，能访问 Windows 凭据管理器。

**用法：**
```bash
cmd /c "C:\Progra~1\Git\bin\bash.exe -l 脚本路径.sh"
```

**禁止用法（永远别用）：**
```powershell
# ❌ 错误示例 - 永远别用
powershell -Command "cd ...; git add -A; git commit -m '...'; git push"
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
- **RYM 优先用 CloakBrowser + RYM Tool**（见下方）
- 其他 CF 站用 opencli + CDP
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

### RYM (RateYourMusic) ⭐⭐ CloakBrowser 方案
- **网址**：https://rateyourmusic.com
- **有 Cloudflare 保护**，`web_fetch` / 普通 Playwright 全部 403/503
- **唯一可用方案**：CloakBrowser + `rym_tool.py`

**安装依赖**：
```
C:\Python311\Scripts\pip.exe install cloakbrowser
```

**脚本**：`C:\Users\qujt\.qclaw\workspace\rym_tool.py`

**用法**：
```
C:\Python311\python.exe rym_tool.py "专辑名" "艺人名"
```

**输出**：
- JSON 文件（专辑名、艺人、评分/5、评价数、流派、风格）
- 截图（搜索页 + 专辑页）

**关键规则（已验证，不可违反）**：
1. `launch(headless=False)` — 必须 headless=False，headless 被 CF 识别
2. 首页等 20 秒 — CF challenge 完成需要时间，不可跳过
3. 搜索框选择器 `#ui_search_input_main_search` — 稳定可用
4. **进入专辑页必须用 JS `link.click()`，不能用 `page.goto()`** — 直接跳转被 CF 503
5. 提取用正则 from `page.content()` — JS 动态渲染，locator 不可靠
6. `delay=60` 模拟人工输入速度

**实测成功**（2026-06-08）：
- Car Seat Headrest - Twin Fantasy: 3.82/5, 22,077 ratings
- The Cure - Disintegration: 4.26/5, 59,795 ratings
- Sonic Youth - Daydream Nation: 4.04/5, 44,124 ratings
- Paul McCartney - The Boys of Dungeon Lane: 3.42/5, 1,616 ratings

**已知限制**：
- 评论数（Reviews）提取不稳定
- 风格（Style）经常提取不到
- 每张专辑约 50-60 秒（CF 等待占大头）
- 单次只能抓一张专辑

### RYM 风格/流派树抓取 ⭐（2026-06-10 验证）

**目标**：获取 RYM 任意流派的完整子流派树形结构

**方法**：CloakBrowser + `/genre/{slug}/` 页面

**关键步骤**：
1. `launch(headless=False)` → 首页等 30 秒过 CF
2. **用 `window.location.href = '/genre/{slug}/'` 导航**（不用 `page.goto()`，会被 CF 503）
3. 等 25 秒让页面加载完成
4. 用正则提取所有子流派链接：`href="/genre/([^"]+)"[^>]*>([^<]+)</a>`
5. 过滤出包含目标流派 slug 的链接即为全部子流派

**已验证数据**（2026-06-10）：
- Rock: **81 个子流派**（9 大分支：Early/Garage/Indie/Folk/Psych/Hard/Glam/Industrial/Regional）
- Genres 首页 (`/genre/`) 是卡片目录，不是树形视图，展开后 2776 个唯一流派但 `<li>` 嵌套深度不可靠
- **单流派页面** (`/genre/rock/` 等) 才列出完整的直接子流派列表

**重要发现**：
- `<a>` 链接文本 = 流派名 ✅ 正确
- `img alt` 属性 = 专辑封面描述 ❌ 不是流派名（如 "Kendrick Lamar - To Pimp a Butterfly, Cover art"）
- Hierarchy 区域的 "Expand Hierarchy" 按钮点击后数量不变（页面已列出全部）
- RYM 流派树是**扁平列表**（一层子流派），非多层嵌套

### Metal-Archives
- **网址**：https://www.metal-archives.com
- **注意**：需 opencli + CDP 绕过 Cloudflare

## 视频背景图生成脚本（V项目）

### ✅ 敲定版参数（V3最终版，2026-06-27）

| 参数 | 值 |
|------|-----|
| 脚本 | `tasks/v-project/_gen_batch_bg_v3.py`（V2底子+动态配色） |
| 输入 | `tasks/v-project/cover_sources/input/` |
| 输出 | `tasks/v-project/output/bg/`（PNG，1920×1080） |
| 尺寸 | 1920×1080（16:9） |
| 构图 | 封面左侧 180px，居中；封面尺寸 550px；右侧留文字区 |
| 模糊 | GaussianBlur radius=30 |
| 暗角 | vignette 强度 0.75 |
| CD外圈 | 深色边框(16px) + 细线(#3C3240) |
| CD内圈 | 圆环(inner_r=55, hole_r=14) |
| 镜面高光 | 左上角弧形白带 |
| 右侧渐暗 | fade_x=封面右边缘+80px |
| 右上装饰 | 三颗圆点（从封面提取主色，非固定金色） |
| 封面边框 | 金色分隔线（从封面提取主色） |

### Linux 快速生成
```bash
cd /root/qclaw/tasks/v-project
python3 _gen_batch_bg_v3.py --input cover_sources/input/ --output output/bg/
# 单张测试: python3 _gen_batch_bg_v3.py --test 封面路径.jpg
```

## RYM 抓取工具（2026-07-20 定稿）

### 核心策略：computer_use 开门 → Selenium 抓数据

CloakBrowser 已废弃，不再使用。

### ✅ 敲定方案

| 步骤 | 工具 | 用途 | 速度 |
|------|------|------|------|
| 1. 开门 | computer_use + 真实 Firefox | 通过 CF 验证，生成 cf_clearance | 慢但只做一次 |
| 2. 抓取 | Selenium + Firefox profile | 复用 cookie，快速提取数据 | 秒级 |

### Selenium 快速抓取

```bash
python tasks/rym-expert/_rym_charts_selenium.py
```

### 环境依赖
- geckodriver v0.37.0（`/usr/local/bin/geckodriver`）
- selenium（`pip install selenium`）
- Firefox profile: `3pdxe3s8.default-esr`

---

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

_Last updated: 2026-06-08_
