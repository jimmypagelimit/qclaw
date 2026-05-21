# MEMORY.md - 长期记忆（精简版）

## 用户信息
- Name: 张树 (jim)，山东济南，Asia/Shanghai
- 音乐偏好: 独立音乐，Car Seat Headrest、刺猬乐队、张悬(安溥)、Sonic Youth、反光镜、U2
- 听歌轨迹: 2011(高一)开始听许巍《在别处》→一路到2018《无尽光芒》，7年弧线；2013(大一)听雷光夏
- 年龄锚点：2008年初二(13岁)，2012高三(17岁)，2016大四(21岁)

## 音乐库
- 源目录: G:\音乐编年史
- 荒岛唱片: H:\私人\荒岛唱片 (主) + C:\荒岛唱片 (副本)
- 岁月新歌⭐: G:\diary-content\history\music\list\岁月新歌\（2005-2024）
- 岁月拾歌⭐: G:\diary-content\history\music\list\岁月拾歌\（2008-2024）
- **双螺旋**：新歌=世界给了你什么，拾歌=你真正要什么
- **详解**：→ `MEMORY-听歌脉络详解.md`

## 审美DNA（三条铁律，13岁到30岁未变）
1. **有"人的气息"** — 创作>流水线
2. **有"超越此刻"的东西** — 非纯娱乐
3. **有"不驯服"的姿态** — 不顺从、不安全、不取悦

## B站账号
- 郊眠寺墨麒麟，104视频(RYM榜单)，1336粉/1.8万赞/58.4万播放

## 重要规则

### 荒岛唱片同步 ⭐
- 互相补充模式：只补充不删除，H盘C盘都同步
- 脚本: H:\私人\荒岛唱片\sync.sh

### 飞书
- 文件拖群不私信，xlsx先复制到workspace再发
- 独立音乐动态发私聊: user:ou_b9a6b98a8be0c723b1719ba17c78df2d

### 翻译
- **不调外部翻译API**，我自己翻

### Kindle
- 格式EPUB，必须带图片排版，邮箱 JIMMYPAGELIMIT_ACFYFR@KINDLE.com
- 主题"Convert"，附件名"attached.epub"

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
- 命令执行优先级: Python > PowerShell > Git Bash

## 原创计划
- 路径: G:\原创计划
- 月度/专题/年榜/双面计划/听歌随想/新专速递

### 听歌记录数据库（album-tracker 项目）⭐ 长期维护
- **SQLite**: G:\原创计划\music
- **CLI 工具**: {workspace_root_dir}\tasks\2026-05-12-long-term-project\album-tracker
- **Web 界面**: http://localhost:3456（`node dist/server.js` 启动）
- **Python 3.11**: C:\Python311\python.exe
- **统计规则**: 总排行查 albums 表，年度排行查 albums_YYYY 表
- **数据库现状**: albums 495条 | albums_2026 122条

### 听歌记录维护流程（2026-05-12 起 ⭐ 终身维护）
- **用户不再维护 Markdown**，改为直接告诉我要听/已听的专辑
- 我直接操作数据库（Web界面或API/CLI）
- **双表同步**：写入年份表 + albums 总表
- **同步规则**:
  - 专辑不存在 → 新增记录
  - 专辑已存在 → **只增加** `total_listen_count`（判重依据：album_name + artist）
- Markdown 文件已清空，仅保留空文件占位
- 导入脚本: `album-tracker/scripts/import_2026.py`（默认华语新+外语新，`--all`全四类）

## 常用网站
- 匿名旅行者: https://www.anontraveler.com（音乐流派百科）

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

## 未完成任务
- AOTY周五推送cron：需在QClaw UI手动创建
