# HEARTBEAT.md

# 定期任务检查清单

> **投递目标**：所有 heartbeat 提醒统一发到本群 `oc_85fa2f97d8d5d3b11eedad80146293e6`

## 🪞 输出质量反思（每日）

- 每日首次 heartbeat 回顾昨日输出，自检：
  - 有无过程堆砌？（搜索过程该省就省）
  - 有无信息轰炸？（视觉层次清晰吗）
  - 有无过度解读？（没问的别主动加）
  - 有无废话？（"让我试试"之类的删掉）
- 发现问题→记入 memory，下次改进

## 🖼️ 专辑封面每日补全（album-tracker）

- **脚本**: `cd C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker; node dist/download-covers.js --count 10`
- **每天至少 10 张**，按排名顺序（收听次数+评分高的优先）
- 来源优先级：iTunes > Deezer > 网易云
- 需先停 Web 服务器（sql.js 内存模型独占写），下载完再重启
- 完成后飞书通知结果
- 无需用户提醒，主动执行

### heartbeat-state.json 追踪
```json
{
  "lastChecks": {
    "covers": 0,
    "covers_total": 216,
    "covers_remaining": 279,
    "c_drive_check": "2026-06-08"
  }
}
```

---

## 💿 荒岛唱片每日同步

- 每日首次 heartbeat 检查 H 盘和 C 盘是否挂载
- 已挂载 → 执行 sync.sh（只补充不删除，互相补充模式）
- 未挂载 → 跳过，下次 heartbeat 再检查
- 同步完成 → 飞书通知结果
- 无需用户提醒，主动执行

## 📋 每日工作总结与推送（~17:00）

- 每日约17:00 heartbeat 时执行
- 汇总当日完成的工作（memory/2026-MM-DD.md + git diff）
- commit + push workspace 仓库
- 飞书通知：当日工作摘要 + 推送状态
- 无需用户提醒，主动执行

## 💾 C盘空间监控（每天）

- **阈值**：C 盘已用空间 > 50GB 时飞书告警
- **检查频率**：每日首次 heartbeat
- **检查方法**：Python `shutil.disk_usage("C:\\")`
- **告警格式**：⚠️ C盘占用告警 | 当前已用：XX.X GB | 当前剩余：XX.X GB
- **正常时不发通知**（避免骚扰）
- **heartbeat-state.json 追踪**：记录 `lastChecks.c_drive_check`

### Python 检查代码（用于 heartbeat）
```python
import shutil
usage = shutil.disk_usage("C:\\") 
used_gb = usage.used / (1024**3)
free_gb = usage.free / (1024**3)
if used_gb > 50:
    print(f"⚠️ C盘占用告警 | 当前已用：{used_gb:.1f} GB | 当前剩余：{free_gb:.1f} GB")
```

## 🌿 身心保养提醒

- **周日身心回顾（20:00-21:30）**：花3分钟回顾本周身心状态
- **每月1号月度评估（9:00-11:00）**：回顾上月整体状态
- 同一条提醒每天只发一次，深夜（23:00-7:00）不打扰

### heartbeat-state.json 追踪
```json
{
  "lastChecks": {
    "rss": 0,
    "weekly_review": "2026-06-08",
    "monthly_review": "2026-05-01",
    "c_drive_check": "2026-06-08",
    "covers": 0,
    "covers_total": 216,
    "covers_remaining": 279
  }
}
```

---

## 🎵 独立音乐动态 (每天)

**RSS 源完整列表见 `RSS-SOURCES.md`**，这里只写检查逻辑。

### 轮换策略
- **周一三五**：Indie 线 — Pitchfork + Stereogum + Consequence + NME + BrooklynVegan + Post-Punk.com + Aquarium Drunkard + r/indieheads + r/shoegaze + r/postrock + r/noiserock + r/postpunk
- **周二四六**：Metal/Hardcore 线 — Decibel + No Clean Singing + Angry Metal Guy + Invisible Oranges + Lambgoat + No Echo + r/Metal + r/blackmetal + r/experimentalmusic
- **周日**：深挖线 — Bandcamp Daily + Paste + Quietus + The Line of Best Fit + Metal-Hammer.de + Toilet Ov Hell + UPEE + r/LetsTalkMusic + r/indie_rock
- **UPEE**：每天扫（更新低，约每周1-2篇）

### 重点关注
- 荒岛唱片收藏艺术家新发行/巡演/新闻
- 重量级新专辑（评分 8.5+）
- 地下金属新发现 / 硬核朋克圈动态 / Bandcamp 独立发行

### 通知
每次检查完都发飞书。格式：🎸 Indie / 🔥 Metal / 🤘 Hardcore / 🌊 Experimental
无重大更新：「今日独立音乐动态：无重大更新」

---

## 📚 文学动态（每周2-3次）

**RSS 源完整列表见 `RSS-SOURCES.md`**，这里只写检查逻辑。

### 三层抓取架构
| 层级 | 方式 | 频率 | 覆盖 |
|------|------|------|------|
| **RSS 自动** | web_fetch RSS | 每周2-3次 | 英文21源 + 中文2源 |
| **网页抓取** | web_fetch 页面 | 每周1-2次 | 新京报文化、凤凰读书、澎湃、中国作家网等 |
| **CDP 浏览器** | browser 工具 | 每周1次或按需 | 界面文化、南方周末等 JS 渲染站 |

### 轮换策略
- **周一**：英美+非洲+日本 — NY Review of Books + Literary Hub + Guardian Books + Electric Literature + Brittle Paper + LH日本tag + r/literature + r/TrueLit
- **周三**：中文网页+韩国+东南亚 — web_fetch 新京报/澎湃/中国作家网/中国诗歌网/朝日好書好日 + RSS: The Millions + Full Stop + Words Without Borders + 韩民族日报 + Korean Lit Blog + Asia Sentinel + New Naratif + r/WorldLiterature + r/ChineseLanguage
- **周五**：欧洲+大洋洲+俄罗斯+左翼 — The New Yorker + Harper's + Eurozine + Le Monde diplo + Meanjin + Granta + Meduza + New Left Review + Jacobin + r/poetry + r/AskLiteraryStudies
- **周末（可选）**：诗歌+科幻+言论自由 — Clarkesworld + Orion + Conjunctions + Reactor + Index on Censorship + Chinese Pen

### 重点关注
- 重要文学奖项（诺贝尔/布克/普利策/龚古尔/芥川/鲁迅/茅盾）
- 重量级新出版物 / 中文翻译文学新译本
- 诗歌+自然写作 / 科幻新作品
- ⭐ 山东地方文学（山东文学/青岛文学/万松浦）

### 通知
每周2-3次汇总。格式：📖 书评 / 🏆 奖项 / ✍️ 创作 / 🌏 翻译 / 🚀 科幻 / 🏔️ 山东
无重要更新不发。

---

## 🏛️ 历史哲学动态（每周1-2次）

**RSS 源完整列表见 `RSS-SOURCES.md`**，这里只写检查逻辑。

### 轮换策略
- **周二（历史日）**：History Today + History Extra + History Workshop + Smithsonian + OUP History + World History Encyclopedia + Medievalists.net + CSSN历史学 + r/AskHistorians + r/history + r/HistoryofIdeas + r/ChineseHistory + r/medihist
- **周四（哲学日）**：Aeon + Philosophy Now + Philosopher's Magazine + Daily Nous + Electric Agora + OUP Philosophy + n+1 + Dissent + r/philosophy
- **周末（可选：地缘+政治哲学）**：Foreign Affairs + Journal of Democracy + New Criterion + Commentary + Persuasion + 豆瓣书评 + 阮一峰

### 重点关注
- 历史学新著/新发现 / 哲学前沿（伦理/政治/科技哲学）
- 🇨🇳 中国历史研究动态 / 中世纪/古代文明考古
- 民主/威权/政治制度讨论

### 通知
每周1-2次汇总。格式：📜 历史 / 🧠 哲学 / 🏛️ 政治思想
无重要更新不发。

---

## ⛪ 宗教动态（每周1次）

**RSS 源完整列表见 `RSS-SOURCES.md`**，这里只写检查逻辑。

### 轮换策略
- **周六（宗教日）**：Lion's Roar + Tricycle + Buddhism StackExchange + Christianity Today + Religion News + Islam21c + Jerusalem Post + JNS + Times of Israel + Forward + World Sikh News + Sikh Siyasat + Reddit宗教社区

### 重点关注
- 各宗教重要新闻/事件
- 宗教间对话 / 宗教与政治
- 佛教禅修/冥想动态 / 犹太教文化
- 锡克教社区新闻

### 通知
每周1次汇总。格式：🕊️ 佛教 / ✝️ 基督教 / ☪️ 伊斯兰教 / ✡️ 犹太教 / ☬ 锡克教
无重要更新不发。
