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

## vivo Xplay6 手机探索（2026-08-13）

### 手机信息
- 型号：vivo Xplay6 (PD1610)，Android 7.1.1 (API 25)，6GB RAM
- 序列号：868b722f，USB 连接，屏幕 1080x1920
- 存储：/data 52G 总，23G 已用，29G 可用 (44%)
- 无 root（su 不可用）

### 已完成
- **存储优化**：清理缓存 ~130M（相册缓存38M、vivo.hybrid安装包80M、系统缓存3.4M）
- **存储分析**：Music 16.2G (95%)，相机 431M，snaptube 194M；flac 222个、wav 42个、m4a 123个
- **MTP 挂载**：`/run/user/0/gvfs/mtp:host=vivo_vivo_Android_Phone_868b722f/内部存储设备/`
- **Android 开发环境**：JDK 21 + Android SDK (/opt/android-sdk) + build-tools 30.0.3 + platform-25
- **HelloApp 测试**：成功构建、签名、安装、启动（修复了 R.java 生成、View→TextView 转型、dex 路径）
- **vivo 安装机制**：首次 adb install 会弹确认框需输密码（rc:-200），后续安装只需点"安装"；`install_broadcast_control=0` 可关闭 vivo 安装广播控制
- **锁屏禁用**：`settings put secure lockscreen.disabled 1`，需重启生效，屏幕超时 30 分钟
- **music-dl**：已在 8080 端口启动 web 模式，手机可访问

### album-tracker 安卓化评估
- **结论**：必要性不大，Web 版已够用（手机浏览器可访问电脑 3456 端口）
- **技术可行**但数据同步是最大障碍（单机应用变多端）
- **更实际的利用**：手机直接访问 music-dl (8080) + adb 推送音乐

### Apple Music ALAC 下载器探索（搁置）
- **项目**：https://github.com/alacleaker/apple-music-alac-downloader
- **原理**：Frida hook Apple Music Android 版，拦截 FairPlay DRM 解密，提取 ALAC 无损音频
- **需要**：无 Google APIs 的 Android 模拟器 + Apple Music 订阅 + Frida
- **已安装**：Go 1.24.4、Frida 17.17.0、Android 模拟器 37.2.4、API 30 x86_64 系统镜像
- **障碍**：
  1. Apple Music 6.5.1 只有 ARM 库（armeabi-v7a），x86_64 模拟器无 ARM 翻译
  2. 原始版本 3.6.0 beta 4 无法从网上下载（APKMirror 有反爬）
  3. vivo Xplay6 无 root，无法运行 Frida server
  4. agent.js hook 的函数名（`SVFootHillSessionCtrl::getPersistentKey`）在 6.5.1 中不存在
- **关键函数**（6.5.1 中存在）：`SVFootHillSessionCtrl::instance`、`decryptContext`、`NfcRKVnxuKZy04KWbdFu71Ou`
- **搁置原因**：ARM 设备需 root + x86 模拟器无法运行 ARM 应用，两个条件都不满足
- **重启条件**：找到有 root 的 ARM 设备，或找到可下载的 3.6.0 beta 4 APK