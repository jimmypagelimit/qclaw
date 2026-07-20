# MEMORY.md — 长期记忆（纯 Linux 版）

## 用户信息
- Name: 张树 (jim)，山东济南，Asia/Shanghai
- 音乐偏好: 独立音乐，Car Seat Headrest、刺猬乐队、张悬(安溥)、Sonic Youth、反光镜、U2
- 听歌轨迹: 2011(高一)开始听许巍《在别处》→一路到2018《无尽光芒》，7年弧线；2013(大一)听雷光夏
- 年龄锚点：2008年初二(13岁)，2012高三(17岁)，2016大四(21岁)

## 音乐库
- 双螺旋：新歌=世界给了你什么，拾歌=你真正要什么
- 详解：→ `MEMORY-听歌脉络详解.md`

## B站账号
- 郊眠寺墨麒麟，104视频(RYM榜单)，1336粉/1.8万赞/58.4万播放

## A项目 — album-tracker ⭐ 核心
- **位置**: `/root/qclaw/tasks/2026-05-12-long-term-project/album-tracker/`
- **数据库**: `_music_latest.db`（项目根目录，sql.js 内存数据库）
- **Web 服务**: `http://localhost:3456`（`node dist/server.js` 启动）
- **当前数据**: 563 张专辑，1185 次收听
- **封面目录**: `album-tracker/public/covers/`
- **UI**: Editorial/Magazine 风格，Cormorant Garamond + IBM Plex Sans

### 数据库操作铁律（2026-07-14 确立）
**写操作：必须用 API（POST/PUT/DELETE），永远不 kill**
- POST /api/albums — 新增专辑 + 自动加 listen
- POST /api/albums/:id/listen — 追加收听次数
- PUT /api/albums/:id — 更新专辑信息
- sql.js 是内存数据库，改完要 reload 才能同步

**查操作：随意，可以 kill 也可以直接读 DB**

### 专辑入库同步规则（2026-06-08 重构）
每次新增专辑时执行完整流程：
1. ✅ 写入 `albums` 表 + `listen_history` 表
2. ✅ 繁简转换（繁体入库先转简体）
3. ✅ 下载封面（iTunes > Deezer > 网易云）
4. ✅ 复制封面到 `public/covers/`
5. ✅ 更新数据库 `cover_image_url` 字段
6. ✅ 重启 Web 服务（sql.js 内存数据库需要 reload）

**判重依据**：`album_name + artist`（非 `album_id`）

### 繁简转换规则
繁体入库的专辑必须先转为简体
- 无歧义自动转换：並→并、於→于、體→体、會→会、後→后
- 有歧义人工核对：`著`（著名 vs 看着）、`干`（干净 vs 干部）

### 封面来源优先级
1. iTunes Search API — 主力，600x600
2. Deezer API — 中文专辑补充
3. 网易云 API — 中文独立/地下乐队
4. MusicBrainz Cover Art Archive — 备选

## RYM 抓取工具
- 路径: `/root/qclaw/tasks/rym-expert/`
- 用法: `rym_tool.py "专辑名" "艺人名"`
- 关键规则: headless=False，首页等20秒
- 只能在本地 Linux 运行（需要 CloakBrowser）
- **禁止批量爬取**，只能单专辑查询

## 歌词专家项目
- **位置**: `/root/qclaw/tasks/lyrics-expert/`
- **歌词目录**: `lyrics/{Artist}/{Album}/`（.lrc + .txt）
- **曲目表目录**: `tracklists/`
- **LRCLIB**: 英文歌命中率接近100%
- **网易云**: 中文歌词主力源

## 常用网站
- 匿名旅行者: https://www.anontraveler.com（音乐流派百科）
- RYM: https://rateyourmusic.com（需 CloakBrowser 绕 CF）

## 联系方式
- 邮箱: 15206651142@163.com
- Kindle: JIMMYPAGELIMIT_ACFYFR@KINDLE.com

## 技术配置（纯 Linux）
- Node.js 24.15.0
- 数据库: sql.js（内存）+ _music_latest.db 文件
- 进程管理: 直接后台启动（background=true）
- Git: 本地 git，无 credential helper（需手动处理）

## 身体保养计划（2026-05-01起）
- 晨间：洗脸+面霜+防晒 | 晚间：洁面+保湿+早睡
- 每周日回顾，每月1号月度评估

## 听歌脉络报告
- `岁月新歌×拾歌-听歌脉络深度分析报告-2008至2026-双线合璧版.md`
- `听歌轨迹十年预测-2025至2035.md`
- 核心预测：自由爵士2030年出现，2032年可能开始声音创作

## 用户身份与偏好
- 张树家二孩出生（2026年6月前后）
- 很少喜欢直男音乐，喜欢女声、男同、女同歌手
- 音乐生命才是真正的生命
- 支持queer

## 经验与决策
- style=大类（Rock/Pop/Folk/Punk/Metal），genre=细分类
- 删除是自己的锅，要承认。不甩锅给用户的指令格式
- 任何数据操作（增删改）必须先确认用户意图
- `trash` > `rm`（可恢复胜过永远消失）