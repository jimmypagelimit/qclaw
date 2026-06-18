# MEMORY.md - 长期记忆（精简版）

## 用户信息
- Name: 张树 (jim)，山东济南，Asia/Shanghai
- 音乐偏好: 独立音乐，Car Seat Headrest、刺猬乐队、张悬(安溥)、Sonic Youth、反光镜、U2
- 听歌轨迹: 2011(高一)开始听许巍《在别处》→一路到2018《无尽光芒》，7年弧线；2013(大一)听雷光夏
- 年龄锚点：2008年初二(13岁)，2012高三(17岁)，2016大四(21岁)

## 音乐库
- 源目录: \\10.0.2.4\qemu\音乐编年史
- 荒岛唱片: 已废弃，不再维护
- 岁月新歌⭐: \\10.0.2.4\qemu\diary-content\history\music\list\岁月新歌\（2005-2024）
- 岁月拾歌⭐: \\10.0.2.4\qemu\diary-content\history\music\list\岁月拾歌\（2008-2024）
- **双螺旋**：新歌=世界给了你什么，拾歌=你真正要什么
- **详解**：→ `MEMORY-听歌脉络详解.md`

## B站账号
- 郊眠寺墨麒麟，104视频(RYM榜单)，1336粉/1.8万赞/58.4万播放

## 重要规则

### 专辑入库同步规则（2026-06-08 重构）
**每次用户新增专辑时，必须执行完整流程：**
1. ✅ 停止 Web 服务（避免 sqlite3 锁冲突）
2. ✅ 写入 `albums` 总表 + `listen_history` 表（年度表已废弃）
3. ✅ 繁简转换（繁体入库必须先转简体，见下方规则）
4. ✅ 下载封面（iTunes > Deezer > 网易云，保存为 `{id}-{artist}-{album}.jpg`）
5. ✅ 复制封面到 `album-tracker/public/covers/`（Web 访问路径）
6. ✅ 更新数据库 `cover_image_url` 字段为 `/covers/{filename}.jpg`
7. ✅ 导出 `database.sql`
8. ✅ Git add + commit + push

**判重依据**：`album_name + artist`（非 `album_id`）
**单表模式**：只操作 `albums` + `listen_history`，不再使用年度表

### 繁简转换规则（2026-05-27 确立）⭐
**核心原则**：繁体入库的专辑必须先转为简体
- ✅ 无歧义字符自动转换：並→并、於→于、體→体、會→会、後→后、學→学、門→门、國→国等
- ⚠️ 有歧义字符需人工核对：`著`（著名 vs 看着）、`干`（干净 vs 干部）
- 📝 转换脚本：`_convert_traditional_v2.py`（无歧义映射表）
- 🔍 人工核对：转换后搜索含`著`的记录，逐条确认

### 封面文件路径规则（2026-05-27 确立）⭐
**Web 访问路径**：`album-tracker/public/covers/{filename}.jpg`
**备份路径**：`\\10.0.2.4\qemu\原创计划\covers\`（仅备份，不直接访问）
**数据库字段**：`cover_image_url = '/covers/{filename}.jpg'`
**常见错误**：
- ❌ 封面文件只放在备份路径，未复制到 `public/covers/` → HTTP 404
- ❌ `cover_image_url` 字段为 `None` → Web 界面不显示封面

### 命令执行规则（2026-05-27 确立）⭐
**永久禁用 PowerShell**（用户明确要求："杜绝使用powershell"）

**执行优先级**：
1. **Python** — `C:\Python311\python.exe`（绝对第一，所有任务优先用 Python）
2. **Node.js** — `node`（仅当 Python 不合适时用，如 album-tracker CLI）
3. **CMD** — `cmd /c "..."`（仅简单命令，Python 无法处理时）
4. **Git Bash** — `cmd /c "C:\Progra~1\Git\bin\bash.exe -l ..."`（仅 Git 操作）
5. ~~PowerShell~~ ❌ **永久禁用，永远别用**

**Git 操作必须用 Git Bash**（原因：有 credential helper，能访问 Windows 凭据管理器）

### 荒岛唱片维护 ⭐
- 位置: \\10.0.2.4\qemu\荒岛唱片（G: 盘）
- 手动管理，无自动同步【H: 盘已废弃】

### 飞书
- 文件拖群不私信，xlsx先复制到workspace再发
- 独立音乐动态发私聊: user:ou_b9a6b98a8be0c723b1719ba17c78df2d

### 翻译
- **不调外部翻译API**，我自己翻

### Kindle
- 格式EPUB，必须带图片排版，邮箱 JIMMYPAGELIMIT_ACFYFR@KINDLE.com
- 主题"Convert"，附件名"attached.epub"
- total_listen_count 字段已彻底删除，收听次数完全从 listen_history 实时计算
- 下载封面（网易云API > iTunes > Deezer > MusicBrainz Cover Art Archive），绝对禁止用网页截图

## 联系方式
- 邮箱: 15206651142@163.com（授权码: WWPkQKMPCMP4TPpx）
- Kindle: JIMMYPAGELIMIT_ACFYFR@KINDLE.com

## 技术配置
- Python: C:\Python311\python.exe (3.11.9)
- pip: C:\Python311\Scripts\pip.exe (阿里云源)
- ffmpeg: C:\ffmpeg\ffmpeg.exe (8.1.1)
- Everything HTTP: localhost:18000 (便携版 C:\Everything)
- 浏览器: OpenClaw 内置 Chromium（browser 工具）
- Git操作用 Git Bash（有credential helper），不用PowerShell
- 命令执行优先级: Python > Node.js > CMD > Git Bash（PowerShell 永久禁用）

## L项目（Lyrics Expert）⭐ 2026-06-15 确立
- **位置**: `tasks/lyrics-expert/`
- **管道**: Playwright(MusicBrainz曲目表) → LRCLIB(歌词) → 本地保存
- `lyrics_pipeline.py`: 完整歌词获取管道（搜索MB→选release→提取曲目→LRCLIB获取歌词→保存到lyrics/）
- `mb_playwright.py`: 仅MusicBrainz曲目表提取（供后续调用）
- `mb_tracklist.py`: 独立曲目提取脚本
- **歌词目录**: `tasks/lyrics-expert/lyrics/{Artist}/{Album}/`（.lrc时间戳歌词 + .txt纯文本）
- **曲目表目录**: `tasks/lyrics-expert/tracklists/`
- **已验证成功**: Car Seat Headrest - Twin Fantasy (10/10首，18个文件)
- **MusicBrainz曲目表获取方法**:
  1. Playwright搜索release-group（search?type=release_group&method=indexed）
  2. 选Album类型（跳过Remix/Single）
  3. 打开release-group页面 → 找 `table.tbl.mergeable-table` → 提取release行（`/release/xxx/cover-art` 去掉/cover-art后缀）
  4. 优先选Digital Media release → 打开release页面 → 提取tracklist（`table.tbl.medium` 中tr的td[0]=序号 td[1]=标题 td[3]=时长）
- **限流注意**: MB频繁请求会被ERR_CONNECTION_CLOSED，需等待冷却
- **MB SSL问题**: API方式urllib/requests SSL失败(UNEXPECTED_EOF_WHILE_READING)，Playwright真实浏览器可绕过
- **LRCLIB**: 英文歌命中率接近100%，无中文歌词
- **扩展方向**: 可接入LyricsTranslate（多语种翻译）和Musixmatch（时间戳对齐）
- **LRCLIB**: 英文歌命中率接近100%，无中文歌词
- **网易云**: 中文歌词主力源，API需Referer头，有翻译歌词+时间戳
- **MB SSL问题**: Windows下间歇性不可用，Playwright可绕过
- **扩展方向**: LyricsTranslate（冷门补充）

## 原创计划
- 路径: \\10.0.2.4\qemu\原创计划
- 月度/专题/年榜/双面计划/听歌随想/新专速递

### 听歌记录数据库（album-tracker 项目）⭐ 长期维护
- **SQLite**: `C:\Users\qujt\.qclaw\workspace\_music_latest.db`（唯一正确路径，2026-06-12确立）
- **CLI 工具**: {workspace_root_dir}\tasks\2026-05-12-long-term-project\album-tracker
- **Web 界面**: http://localhost:3456（`node dist/server.js` 启动）
- **Python 3.11**: C:\Python311\python.exe
- **统计规则**: 总排行查 `albums` 表，年度排行查 `listen_history` + `albums` JOIN（**不再使用年度表**）
- 数据库现状: albums 524条 | MBID覆盖率90.3% | 描述覆盖率97.3% | RYM评分覆盖率25%

### 听歌记录维护流程（2026-06-08 重构 ⭐ 终身维护）
- **用户不再维护 Markdown**，改为直接告诉我要听/已听的专辑
- 我直接操作数据库（Web界面或API/CLI）
- **单表模式**：只操作 `albums` + `listen_history`（**年度表已废弃**）
- **同步规则**:
- 专辑不存在 → 新增记录到 `albums`，写入 `listen_history`
- 专辑已存在 → **只增加** `total_listen_count`，新增 `listen_history` 记录（判重依据：album_name + artist）
- Markdown 文件已清空，仅保留空文件占位
- 导入脚本: `album-tracker/scripts/import_2026.py`（默认华语新+外语新，`--all`全四类）
- [详细操作手册](ALBUM_TRACKER_RULES.md)
- sql.js 是内存数据库，每次改 DB 后必须重启 Web 服务：kill 进程 → 释放端口 → node dist/server.js

## RYM 抓取工具（2026-06-08 确立）⭐
- **CloakBrowser** 绕过 Cloudflare，脚本 `rym_tool.py`
- 用法: `C:\Python311\python.exe rym_tool.py "专辑名" "艺人名"`
- 关键规则: headless=False, 首页等20秒, JS click进入专辑, 正则提取
- 已验证4张专辑成功，详见 TOOLS.md
- RYM 抓取工具（2026-06-15 升级）⭐
- ⭐ 批量禁令（2026-06-16确立）：禁止批量爬取RYM，废除rym_fill_v3.py和所有cron任务；只能单专辑查询（rym_tool.py）
- **单专辑查询**：`rym_tool.py`
- CloakBrowser绕CF，headless=False，正则提取avg_rating
- 评分字段：`rymv2_score`（float）

## 常用网站
- 匿名旅行者: https://www.anontraveler.com（音乐流派百科）
- RYM: https://rateyourmusic.com（需 CloakBrowser 绕 CF）

## 身体保养计划（2026-05-01起）⭐
- 晨间：洗脸+面霜+防晒 | 晚间：洁面+保湿+早睡
- 每周日回顾，每月1号月度评估

## 听歌脉络报告（2026-05-01）
1. `岁月新歌×拾歌-听歌脉络深度分析报告-2008至2026-双线合璧版.md`
2. `听歌轨迹十年预测-2025至2035.md`
- 核心预测：自由爵士2030年出现，2032年可能开始声音创作

## RSS体系（2026-05-01建成）
- 153源：44音乐+62文学+25历史哲学+22Reddit
- 详见 `RSS-SOURCES.md`，检查逻辑见 `HEARTBEAT.md`

## 用户身份与偏好

- 张树家二孩出生（2026年6月前后）

## 经验与决策

- style=大类（Rock/Pop/Folk/Punk/Metal），genre=细分类（RYM 细类）
- 删除是自己的锅，要承认。不要甩锅给用户的指令格式，检查自己有没有正确理解
