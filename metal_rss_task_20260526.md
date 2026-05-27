# Metal/Hardcore RSS 聚合任务报告

## 任务目标
抓取9个 Metal/Hardcore RSS 源，提取最近3天（2026-05-23至2026-05-26）的重要新闻/新专辑/巡演信息。

## 执行结果

### 成功抓取的 RSS 源（9/9）
1. ✅ Decibel Magazine - https://www.decibelmagazine.com/feed/
2. ✅ No Clean Singing - https://www.nocleansinging.com/feed/
3. ✅ Angry Metal Guy - https://www.angrymetalguy.com/feed/
4. ✅ Invisible Oranges - https://www.invisibleoranges.com/feed/
5. ✅ Lambgoat - https://www.lambgoat.com/rss/news
6. ✅ No Echo - https://feeds.feedburner.com/noecho
7. ✅ r/Metal - https://www.reddit.com/r/Metal/.rss
8. ✅ r/blackmetal - https://www.reddit.com/r/blackmetal/.rss
9. ✅ r/experimentalmusic - https://www.reddit.com/r/experimentalmusic/.rss

### 最近3天重要发现

#### 🔥 新专辑（重量级）
- **Monolord - Neverending** (Doom Metal, Relapse Records) - 瑞典厄运金属名团新作
- **Galvanist - The Silence Between Stars** (Sludge/Black/Doom, Independent) - Montana 乐队第二张专辑
- **Funebrarum - Beckoning the Void of Eternal Silence** (Death Metal, Pulverised Records) - 7年等待后的新专辑
- **Trelldom - ...by the word...** (Avant-garde, Prophecy Productions) - Gaahl 参与
- **Elder - Through Zero** (Progressive Rock, Blues Funeral Recordings)
- **Pro-Pain - Stone Cold Anger** (Groove/Crossover, Napalm Records) - 11年来首张新专辑
- **The Fifth Alliance - Stenahoria** (Doom/Black, Tartarus Records)
- **Maladie - The Dance of Tragedies** (Avant-garde Black Metal, Apostasy Records)

#### 💀 地下发现
- **Suffering Quota - "Head"** (Grindcore, Tartarus Records) - 荷兰 grind 乐队新专辑预热
- **Siyahkal - Corrupt / فاسد** (Hardcore Punk, Static Shock Records) - 回应伊朗战争

#### 🤘 巡演新闻
- Parkway Drive 重返录音室
- Knocked Loose 发布夏日巡演日记
- Avatar 官宣欧洲/英国巡演
- Ocean Grove 澳洲巡演（支持：Cane Hill）

#### 📰 其他重要新闻
- Voivod 新现场专辑 *Symphonique*（与魁北克交响乐团合作，6月5日发行）
- Iron Maiden 38年来首次现场表演 "Infinite Dreams"
- Beartooth 主唱 Caleb Shomo 出柜
- Crown Magnetar 发布新单曲 "Impaled Genesis"

## 重点关注事项
- **Bandcamp 独立发行**：Galvanist、Funebrarum、Suffering Quota、Siyahkal 等均在 Bandcamp 有独立或厂牌发行
- **评分8.5+专辑**：本次 RSS 抓取中未明确提及具体评分，但 Monolord、Funebrarum、Galvanist 均获得乐评人高度关注
- **硬核朋克动态**：Siyahkal 新专辑直接回应政治事件，Crown Magnetar 发布新单曲

## 技术笔记
- 所有 RSS 抓取均使用 `web_fetch` 工具
- Reddit RSS 源返回 Atom 格式（application/atom+xml）
- 部分 RSS 源内容被截断（Angry Metal Guy、r/Metal、r/blackmetal、r/experimentalmusic）
- 日期过滤：成功识别并保留 2026-05-23 至 2026-05-26 的内容

## 输出格式
按照要求生成中文汇总，格式为：
- 🔥 Metal/Hardcore 动态 | 2026-05-26
- 每条用 emoji 开头（🔥新专辑 / 🤘巡演 / 📰新闻 / 💀地下发现）

任务完成时间：2026-05-26 06:32 GMT+8
