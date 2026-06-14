# Album-Site 项目 — 音乐数据源档案

> 项目位置：`tasks/album-site/`
> 创建日期：2026-06-14

---

## 数据源一览

| # | 站点 | 类型 | 反爬 | 核心价值 |
|---|------|------|------|----------|
| 1 | The Needle Drop | 乐评 | 无 | Fantano 评分（1-10），独立音乐圈最具影响力 |
| 2 | AllMusic | 元数据 | 无 | 专辑/曲目/厂牌/流派/时长，元数据最全 |
| 3 | NME | 乐评 | 有 CF | 老牌媒体评分，1054页历史存档 |
| 4 | ChartMasters | 流媒体/销量 | 无 | Spotify 播放量、专辑销量、艺术家排行 |
| 5 | Best Ever Albums | 聚合排行 | 无 | 59,000+ 张榜单聚合，综合排名/评分/上榜次数 |
| 6 | Acclaimed Music | 聚合排行 | 有 CF | 聚合千家媒体/评论家评选，历史最佳专辑排行 |
| 7 | Stereogum | 新闻/乐评 | 无 | 独立音乐最活跃博客，RSS 稳定，已纳入 RSS 体系 |

---

## 1. The Needle Drop

- **网址**：https://theneedledrop.com
- **评分体系**：1-10 分（整数或 Light/Decent/Mixed/Strong 等文字评级）
- **核心内容**：专辑评论、新发行亮点、采访、音乐节报道
- **反爬状况**：无 Cloudflare，可直接 web_fetch
- **URL 结构**：
  - 乐评：`/album-reviews/{artist}-{album}-album-review/`
  - 新发行：`/todays-release-highlights-{date}/`
- **页面结构**：WordPress 站点，readability 可提取正文
- **已知数据**：首页可见 Vince Staples Cry Baby、Converge Hum of Hurt、Feeble Little Horse Bitknot 等近期乐评

---

## 2. AllMusic

- **网址**：https://www.allmusic.com
- **评分体系**：1-5 星
- **核心内容**：专辑评论、艺术家传记、新发行推荐、编辑精选
- **反爬状况**：无 Cloudflare，可直接 web_fetch
- **URL 结构**：
  - 专辑页：`/album/{album-name}-mw{id}`
  - 艺术家页：`/artist/{artist-name}-mn{id}`
  - 新发行：`/newreleases`
  - 流派页：`/style/{style-slug}-ma{id}`
- **页面结构**：可提取，含专辑元数据（发行日期、厂牌、时长、曲目列表、流派标签）
- **已知数据**：首页有每日新评论（6/12 日 8 条）、编辑精选（5 月 10 张）、趋势流媒体艺人

---

## 3. NME

- **网址**：https://www.nme.com
- **评分体系**：1-5 星（部分无评分）
- **核心内容**：专辑评论、新闻、榜单、专访
- **反爬状况**：有 Cloudflare，需浏览器方案（CloakBrowser/opencli CDP）
- **URL 结构**：
  - 乐评列表：`/reviews/album`（共 1,054 页）
  - 单篇乐评：`/reviews/album/{artist}-{album}-review-{id}`
- **页面结构**：JS 渲染较多，readability 提取质量中等
- **已知数据**：首页可见 Kelsey Lu、Infinity Song、Vince Staples、Paul McCartney 等近期评论

---

## 4. ChartMasters

- **网址**：https://chartmasters.org
- **数据类型**：流媒体数据、销量排行（非乐评，无评分体系）
- **核心内容**：
  - 最佳销量艺人/专辑/歌曲
  - Spotify 流媒体排行（艺人/专辑/歌曲）
  - YouTube 播放量排行
  - 艺术家 Dashboard（单曲播放量、月听众、粉丝数）
  - 艺术家对比工具
  - 流媒体版税计算器
  - 十年最佳艺人排行
- **反爬状况**：无 Cloudflare，可直接 web_fetch
- **URL 结构**：
  - 艺人 Dashboard：`/artist-dashboard/`
  - 艺人对比：`/compare-artists/`
  - 播放量工具：`/spotify-streaming-numbers-tool/`
  - 最畅销艺人：`/best-selling-artists-of-all-time/`
  - 流媒体艺人：`/most-streamed-artists-ever-on-spotify/`
  - 流媒体专辑：`/spotify-most-streamed-albums/`
- **已知数据**：
  - 最畅销艺人：The Beatles 525.92m EAS
  - 流媒体之王：Taylor Swift 124.95b streams
  - 流媒体专辑之王：Un Verano Sin Ti 23.34b streams

---

## 5. Best Ever Albums

- **网址**：https://www.besteveralbums.com
- **评分体系**：聚合评分（基于 59,000+ 张榜单的综合排名）
- **核心内容**：
  - Overall Chart：史上最佳专辑总榜
  - 分年代榜、分流派榜
  - 专辑详情页含 Rank Score、上榜次数、平均评分
  - 用户评论
- **反爬状况**：无 Cloudflare，可直接 web_fetch
- **URL 结构**：
  - 总榜：`/overall.php`
  - 专辑页：`/thechart.php?a={id}`
- **页面结构**：PHP 动态站，表格数据可直接解析
- **已知数据**：
  - #1 OK Computer (1997), Rank Score 61,170
  - #2 Dark Side of the Moon (1973), Rank Score 57,891
  - #3 Abbey Road (1969), Rank Score 55,558
  - #4 Revolver (1966), Rank Score 47,856
  - #5 A Love Supreme (1975), Rank Score 43,069
  - #6 In Rainbows (2007), Rank Score 41,822
  - #7 Ziggy Stardust (1972), Rank Score 41,777

---

## 6. Acclaimed Music

- **网址**：https://www.acclaimedmusic.net
- **评分体系**：聚合排名（汇集千家媒体/评论家榜单评选）
- **核心内容**：
  - 历史最佳专辑综合排行
  - 分年代、分流派排行
  - 专辑详情含各来源评价数、综合排名
- **反爬状况**：**Cloudflare 全站保护**，需浏览器方案（CloakBrowser/opencli CDP）
- **URL 结构**：
  - 总榜：`/Overall.htm`
  - 专辑页：`/Album/{id}.htm`
- **页面结构**：静态 HTML，结构清晰
- **已知数据**：与 Best Ever Albums 定位类似，但来源更偏专业评论家

---

## 7. Stereogum

- **网址**：https://stereogum.com
- **评分体系**：无统一评分（偶有 A-F 字母评级）
- **核心内容**：独立音乐新闻、新专辑评论、单曲首发、专辑排行（年度50强）
- **反爬状况**：无 Cloudflare，RSS 直接可抓（`/feed/`）
- **URL 结构**：
  - RSS：`https://stereogum.com/feed/`
  - 文章：`/{post_id}/{slug}/{type}/`（type: music/news/reviews）
  - 年度榜：`/lists/stereogums-50-best-albums-of-{year}/`
- **页面结构**：WordPress 站点，首页 JS 渲染但 RSS 可用
- **已知数据**：RSS 已纳入现有 RSS 体系（153源），稳定运行
- **备注**：已在 HEARTBEAT.md 独立音乐动态监控中

---

## 潜在项目方向

| 优先级 | 项目 | 数据源 | 价值 |
|--------|------|--------|------|
| P0 | TND 评分批量抓取 + 入库 | The Needle Drop | 补全 Fantano 评分，与 Pitchfork 对照 |
| P1 | AllMusic 元数据补全 | AllMusic | 厂牌、时长、流派标签补全数据库 |
| P2 | 流媒体数据对照 | ChartMasters | 商业热度 vs 评论口碑 |
| P3 | BEA/AM 聚合榜对照 | Best Ever Albums / Acclaimed Music | 收藏 vs 历史最佳覆盖率 |
| P4 | NME/Acclaimed Music 存档挖掘 | NME / Acclaimed Music | 历史乐评对照（均需 CF 绕过） |

---

_创建日期：2026-06-14_
