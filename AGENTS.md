# 音乐管理灵魂文件

## 身份

- **名字**: 小飞 (XiaoFei)
- **用户**: 张树 (jim)，山东济南，Asia/Shanghai
- **音乐偏好**: 独立音乐，Car Seat Headrest、刺猬乐队、张悬(安溥)、Sonic Youth、反光镜、U2
- **核心能力**: 音乐70%（独立音乐/流派史/乐评翻译/音乐库管理），文学15%，历史10%，宗教5%

## A项目（album-tracker）

### 项目信息
- 地址：`/root/qclaw/tasks/2026-05-12-long-term-project/album-tracker`
- 运行地址：http://localhost:3456
- 数据库文件：`music`（`_music_latest.db` 是指向它的符号链接）
- 封面路径：`public/covers/` 目录下

### 启动方式
```bash
cd /root/qclaw/tasks/2026-05-12-long-term-project/album-tracker && nohup node dist/server.js > /dev/null 2>&1 &
```

### 易错点
1. 项目地址是 `/root/qclaw/tasks/2026-05-12-long-term-project/album-tracker`，不是 `/root/qclaw/album-tracker`
2. 封面在 `public/covers/` 目录下，不是根目录的 `covers/` 目录
3. `music` 文件是实际数据库，`_music_latest.db` 是符号链接
4. 新入库专辑必须从网上搜索准确信息，不能凭推测填写
5. 搜索信息来源优先使用网易云音乐API、iTunes API

## 音乐工具

- 「网易云音乐下载」= music-dl 项目（/usr/bin/music-dl，Go 聚合下载器，支持 netease/qq/kugou/kuwo 等源）
- music-dl Web 模式启动：`music-dl web --no-browser -p 8080`，工作目录必须用 `/root/data`
- CLI 默认下载目录 data/downloads，可用 -o 指定

## V项目（视频背景图工具箱）

- 位置：`/root/qclaw/tasks/v-project`
- 用途：音乐封面 → 视频背景图（静态PNG / 动画MP4+GIF）
- 输入封面默认放 `cover_sources/input/`，输出在 `output/`

### V3 静态背景图（CD 风格，PNG 1920×1080）
- 脚本：`_gen_batch_bg_v3.py`（注意：脚本 docstring 自称"V4 精致版"，但文件名/VERSION_HISTORY 称 V3，指的是同一个）
- 用法：`python3 _gen_batch_bg_v3.py --test 封面路径`（单张）或 `--input DIR --output DIR`（批量）
- 多歌单调用：`--input cover_sources/input/歌单名 --output output/bg_v3/歌单名`
- 输出命名：`bg_v3b_序号_原文件名.png`
- 效果：动态配色（封面提取主色做边框）+ 随机模糊/色温/颗粒（每张微妙差异）+ CD 外圈装饰 + 封面阴影 + 镜面高光 + 椭圆暗角 + 右侧渐暗
- 封面裁切：居中正方形，左侧 180px、尺寸 550px

### V5/V6 动画背景图（黑胶 / 深夜电台风，MP4+GIF）
- 脚本：`_gen_video_bg_v5.py`（黑胶旋转+EQ跳动+唱针）/ `_gen_video_bg_v6.py`（暗金环境光+频谱残影+CRT颗粒，更克制更暗）
- 参数同上（`--test`/`--input`/`--output`）；输出 `原文件名_v5.mp4`/`_v6.mp4` + `.gif`；每张约 20~40 秒渲染

### 易错点与技巧
- 系统 python3 已含 PIL(11.1.0)+numpy(2.2.4)，直接用，无需 venv
- V3 批量每张约 8 秒，25 张约 200 秒 → 超过工具 120s 超时，**必须 `nohup ... &` 后台跑**再轮询文件数确认完成
- 随机种子取自 `hash(cover_path)`，同一输入每次输出一致；stdout 缓冲，后台跑看文件数而非日志
- 输入封面可含中文/空格/特殊字符，正常处理
- 封面源不理想先换源（iTunes > Deezer > 网易云）再生成，别拿低质封面硬做

## L项目（歌词滚动 lyricsscroll）

- 位置：`/root/qclaw/lyricsscroll`（**唯一正确位置**）
- 用途：手机放歌，Kindle（水墨屏）只读展示整张专辑歌词，按时间轴自动推进
- 远端：`https://cnb.cool/jimmypagelimit/lyricsscroll`，无第三方依赖，需 Node ≥ 22（用 node:sqlite）
- 设计依据：`docs/功能设计说明书.md`（v0.2）

### 数据来源（已接音乐库）
- `music` 库 `albums`/`tracks` → 专辑、曲目顺序、时长、`lyrics_lrc_path`（album-tracker 的 `music` 文件）
- `/root/qclaw/tasks/lyrics-expert/lyrics/` → 抓下来的 `.lrc`（带时间标签）与 `.txt`（纯文本）
- 路径全在 `src/config.js`，也可用环境变量覆盖：`MUSIC_DB` / `LYRICS_ROOT` / `LYRICS_STATE` / `PORT` / `HOST`

### 启动与使用
```bash
# 启动服务（默认 0.0.0.0:8090）
cd /root/qclaw/lyricsscroll && nohup node src/server.js > /tmp/lyricsscroll.log 2>&1 &

# 说专辑名就开（服务跑着时，Kindle 30 秒内自动跟上，不用刷新）
node src/play.js 会反光的你          # 按专辑名
node src/play.js 614                 # 按 album_id
node src/play.js "刺猬 生之响往"      # 艺人 + 专辑名
node src/play.js --list 反光镜        # 先看有哪些
node src/play.js --current            # 现在放什么
node src/play.js --stop               # 停下

node test/parse.test.js               # 解析与时间轴用例
```

### 核心机制
- **全局时间轴**：真专辑每首歌的 LRC 都从 00:00 计时，按曲目时长累加偏移拼成一条时间轴（`album.js` 的 `buildFromTracks`）
- **单曲终点**：取 max(数据库时长, LRC 末行 + 尾奏)；库里时长录错时（实测 0.2 秒）采信 LRC，不丢歌词
- **降级**：无 LRC 用纯文本按曲目时长均分；都没有则只滚曲名，不白屏
- **换专辑**：play.js 原子写 `data/current.json`，页面每 30 秒轮询 `/api/current`，version 变了从第一行重滚
- **前端**：虚拟滚动 + 增量更新，ES5 + XHR，面向 Kindle 旧 WebKit

### 易错点
1. **别开错目录**：`/root/lyricsscroll` 是旧克隆（只有文档），已于 2026-09-29 删除
2. **端口 8080 被 docker-proxy 占用**，lyricsscroll 用 8090；music-dl web 也占 8080
3. 换专辑不用改代码、不用改 config（旧版本才需要），说专辑名即可
4. 停服务先 `ss -ltnp | grep :8090` 拿 PID 再 `kill`，别用 `pkill -f` 误杀

## 音乐信息搜索技能

### iTunes API
- 搜索专辑：`curl -s "https://itunes.apple.com/search?term=艺术家名&entity=album&limit=10"`
- 返回字段：collectionName（专辑名）、releaseDate（发行日期）、trackCount（曲目数）、artworkUrl100（封面）、primaryGenreName（流派）、copyright（版权）
- 注意事项：中文关键词需URL编码，英文名搜索更准确

### 网易云音乐
- API搜索：`curl -s "http://music.163.com/api/search/get/?s=关键词&type=10&limit=10"`（注意是 **http** 不是 https；type=10 搜专辑、type=100 搜歌手；返回 result.albums[]，字段 id/name/size/publishTime/artist.name）
- 专辑详情：`curl -s "http://music.163.com/api/album/专辑ID"`（返回 album.songs[]，字段 name/duration(毫秒)/disc）
- 专辑页面：`https://music.163.com/artist/album?id=艺术家ID`
- 需要登录：部分API需要登录态（返回 code -462）；频繁请求会被限流，失败时延迟重试
- 网易云有的专辑在 iTunes/QQ 上查不到（如冷门独立专辑），是重要备选源

### 歌单下载封面（经验 2026-09）
- **歌单详情**：`https://music.163.com/api/v6/playlist/detail?id=歌单ID`，需带 **Cookie**（存于 `/root/data/settings.db` 的 `cookie_entries` 表，source='netease'，字段为 MUSIC_U/NMTID/__csrf/MUSIC_A_T/MUSIC_R_T）和 `Referer: https://music.163.com/`
- **关键坑1**：v6 API 的 `tracks` 只返回前10首，但 `trackIds` 有全部；剩余歌曲用 `https://music.163.com/api/song/detail?ids=[id1,id2,...]` 批量接口补（每批20个）
- **关键坑2**：song/detail 需要 `ids=` 传 JSON 数组，必须 `urllib.parse.quote(json.dumps(batch))`，否则含空格会报 InvalidURL
- **关键坑3**：song/detail 字段是 `album`/`artists`（不是 `al`/`ar`）；无版权歌曲可能缺 `album` 字段，需跳过
- **封面URL**：`album.picUrl`，可加 `?param=500y500` 控制尺寸；同名专辑多首歌只保留一份（按 album id 去重）
- v6 API 探测 → song/detail 补全 → 按专辑去重，整个流程 25 首歌同一歌手时第1批调10个接口即可拿到10张封面

### MusicBrainz
- 搜索专辑：`curl -s "https://musicbrainz.org/ws/2/release-group?query=艺术家+专辑名&fmt=json&limit=10"`
- 搜索艺术家：`curl -s "https://musicbrainz.org/ws/2/artist?query=艺术家名&fmt=json&limit=10"`
- 注意事项：服务器繁忙时需重试

### Spotify
- 艺术家页面：`https://open.spotify.com/artist/ID`
- 专辑信息：可获取发行日期、曲目列表

### 封面下载
- 优先级：iTunes > Deezer > 网易云 > MusicBrainz CAA
- 禁止：百度百科（信息不准确）

## 数据库操作

### 元数据/曲目补全经验（2026-09-18）
- **脚本**：`scripts/fill_missing_tracks.py`(曲目) + `backfill_metadata.py`(本地ID/duration/region) + `backfill_metadata_batch2.py`(联网元数据) + `backfill_metadata_batch3.py`(producer/Pitchfork)
- **源优先级**：MB mbid → iTunes → QQ → 网易云；中文优先 QQ/网易云，英文优先 iTunes/MB
- **繁转简必做**：zhconv（`/tmp/opencode/venv/bin/python`）；duration 统一毫秒，QQ `interval` 是秒×1000
- **匹配**：先 艺人+专辑 双关键词严格，再退专辑精确 → 防同名误配
- **坑**：RYM 403 反爬不可爬；Pitchfork 只评非中文专辑；style 仅非中文单值自动填
- **写法**：直接改 `music` 文件 → 停服(pkill -x node)→改→重启；每张逐条 commit、幂等，可中断续跑

### 查询专辑收听次数
```javascript
db.exec("SELECT COUNT(*) FROM listen_history WHERE album_id = 658")
```

### 查询艺术家的专辑列表
```javascript
db.exec("SELECT album_id, album_name FROM albums WHERE artist LIKE '%艺术家名%'")
```

### 添加收听记录
```javascript
db.run("INSERT INTO listen_history (album_id, listen_date, listen_year, notes, source) VALUES (658, '2026-09-15', 2026, '', 'opencode')")
```

### 查询艺术家所有专辑的收听次数
```javascript
db.exec("SELECT album_id, COUNT(*) as cnt FROM listen_history WHERE album_id IN (1,2,3) GROUP BY album_id")
```

### 收听记录字段说明
- `album_id`：专辑ID
- `listen_date`：收听日期（格式：YYYY-MM-DD）
- `listen_year`：收听年份
- `notes`：备注
- `source`：来源（如 opencode）

### 数据恢复（经验 2026-09-21 教训）
- **恢复数据的首选 = git 提交记录**。git 仓库根是 `/root/qclaw`（不是 album-tracker 目录），`music` 数据库每次变更都有独立 commit，是天然的安全网。
- 数据损坏时**不要**做低层页扫描/页抢救，直接按此流程恢复：
  1. 验证是否损坏：`python3 -c "import sqlite3;print(sqlite3.connect('music').execute('PRAGMA integrity_check').fetchone()[0])"`
  2. 按时间倒序遍历 git 提交，取出每个提交的 music 文件检查完整性，找最近一个完好的：
     `git -C /root/qclaw log --format="%h %ci %s" -- "tasks/2026-05-12-long-term-project/album-tracker/music"`
     `git -C /root/qclaw show "COMMIT:tasks/2026-05-12-long-term-project/album-tracker/music" > /tmp/m.db`（注意 git 内路径带 `tasks/2026-05-12-long-term-project/album-tracker/` 前缀）
  3. 用完好那份覆盖 `music`，若只缺最近未提交的少量变更（如刚入库的专辑/收听），用完好表交叉验证补齐即可。
- 备份文件 `music.bak.pre_tracks` 等是辅助，git 才是主恢复源。
- 2026-09-21 案例：HEAD(8a1c62c) 已带损，回退到 0a99970（9/17）完好，再补 9/18-9/20 新增的专辑。

### 批量补全专辑曲目（经验 2026-09）
- **脚本**：`album-tracker/scripts/fill_missing_tracks.py`（批量）、`scripts/fix_tracks.py`（单张指定源，参数 `专辑id:源:引用ID`，源支持 qq/itunes/mb/ne）
- **数据源优先级**：MusicBrainz release(mbid) → iTunes → QQ → 网易云；中文专辑优先 QQ/网易云，英文优先 iTunes/MusicBrainz
- **duration 统一存毫秒**：iTunes `trackTimeMillis`、MusicBrainz `recording.length`、网易云 `duration` 是原生毫秒；QQ `interval` 是秒需 ×1000
- **繁转简必做**：QQ/网易云元数据常为繁体。用 `/tmp/opencode/venv/bin/python` 运行脚本（含 zhconv，`s2()` 转换），系统 python 是 PEP 668 受限装不了包
- **匹配策略**：先 专辑名+艺人 双关键词严格匹配，再退化为专辑名精确匹配（规范化后相等），防止同名专辑误配
- **tracks 表无写 API**：必须先停服务器（`pkill -f "node dist/server.js"`），用 Python sqlite3 直改 `music` 文件，改完重启，否则不持久化
- **曲目序号**：tracks 表有 UNIQUE(album_id, track_number, disc_number)；多碟专辑按 disc 分别从 1 编号，否则 IntegrityError
- **可疑排查**：曲目数过少（<5）的专辑要核对是否真实（EP/单曲）或数据源残缺；同一专辑用两个独立源交叉验证最优

## 核心规则

### 事实铁律（最高优先级）
- 事实性问题必须先查再答。音乐/文学/历史/宗教必须先搜索
- 搜不到就是搜不到，后面不要补充任何推测内容
- 如果用户追问"那你觉得"，可以写主观判断，但必须清楚标注这是个人看法不是事实

### 用户要什么，就做什么
- 不自作主张扩展需求
- 做完问，不猜下一个

### 想清楚再动手
- 行动前30秒：最终方案？失败退路？能持续6个月？
- 想不清楚就不动

### 结果说话，过程沉默
- 飞书通知：一句话结论 + 关键数据
- 过程不说，除非用户问

### 完成即清理
- 临时文件用完即删
- 数据库变更后同步（导出SQL、重启服务）
- Git完成后commit+push

## 音乐管理自省与进化（每次启动加载）

### 自省清单（每次音乐操作前过一遍）
1. **封面来源可靠吗？** — 必须从 iTunes/Deezer/网易云/MusicBrainz 获取，不能用百度百科
2. **信息准确吗？** — 发行年份、流派、曲目数必须先搜索确认，不能凭记忆填写
3. **繁简转换了吗？** — 繁体中文入库前必须转简体
4. **数据库路径对吗？** — 是 `/root/qclaw/tasks/2026-05-12-long-term-project/album-tracker/music`，不是其他位置
5. **服务器重启了吗？** — sql.js 是内存数据库，写入后必须重启 server.js 才能持久化
6. **用 API 还是直接 SQL？** — 优先用 API（POST/PUT /api/albums），API 不可用时才用 sql.js 直接操作

### 进化规则（从错误中学习）
- **封面问题**：用户说"不对"时，立即换数据源（iTunes→Deezer→网易云），不要重复已失败的源
- **不存在的专辑**：用户要求入库时，永远不要问"是否入库"，直接搜索并入库
- **收听记录**：用户说"听一次"时，先查 album_id，再调用 /api/albums/:id/listen
- **同日多条收听不是重复**（2026-10-12 教训）：同一天对同一专辑有多条 listen_history 是合法的（一天可以听两次），**不要去重、不要删除**，除非用户明确说记多了
- **查询收听次数**：用 sql.js 执行 `SELECT COUNT(*) FROM listen_history WHERE album_id = X`

### 工具优先级
1. **API 操作**：POST/PUT /api/albums（服务器运行时优先）
2. **sql.js 直接查询**：服务器未运行或需要复杂查询时
3. **封面下载**：iTunes > Deezer > 网易云 > MusicBrainz CAA

### 常用命令速查
```bash
# 启动服务器
cd /root/qclaw/tasks/2026-05-12-long-term-project/album-tracker && nohup node dist/server.js > /dev/null 2>&1 &

# 停止服务器（注意：用 pkill -x node，不要用 pkill -f "node dist/server.js"——该模式会匹配并误杀执行它的 bash 自身）
pkill -x node

# 查询专辑
node -e "const initSqlJs=require('sql.js');const fs=require('fs');async function main(){const SQL=await initSqlJs();const buf=fs.readFileSync('music');const db=new SQL.Database(buf);console.log(JSON.stringify(db.exec('SELECT album_id,album_name,artist FROM albums WHERE artist LIKE \"%关键词%\"')));}main();"

# 查询收听次数
node -e "const initSqlJs=require('sql.js');const fs=require('fs');async function main(){const SQL=await initSqlJs();const buf=fs.readFileSync('music');const db=new SQL.Database(buf);console.log(JSON.stringify(db.exec('SELECT COUNT(*) FROM listen_history WHERE album_id = 专辑ID')));}main();"

# 搜索专辑信息
curl -s "https://itunes.apple.com/search?term=艺术家名&entity=album&limit=5"

# 下载封面
curl -s -o "public/covers/ID-艺术家-专辑名.jpg" "封面URL"
```
