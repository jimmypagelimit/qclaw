# 深度翻译管道 v3 - 全覆盖版

## 扩展完成

从9个源扩展到**26个英文乐评源**，覆盖独立/摇滚/民谣/金属。

### 源站清单

#### 🎸 Indie/Rock/Folk（17源，每天5篇）
- Pitchfork、Stereogum、Consequence、Paste、PopMatters
- The Quietus、TLOBF、God Is in the TV、Louder Than War
- AV Club、Spin、Hearing Things、Post-Punk.com
- Bandcamp Daily、MusicOMH、Clash Music、Aquarium Drunkard

#### 🔥 Metal/Hardcore（10源，每天5篇）
- Decibel、Angry Metal Guy、No Clean Singing、Metal Injection
- Invisible Oranges、Toilet Ov Hell、MetalSucks、Metal-Hammer.de
- No Echo、Lambgoat

#### 🌊 Experimental/Underground（8源，每天3篇）
- Aquarium Drunkard、The Quietus、TLOBF、Bandcamp Daily
- PopMatters、Louder Than War、GoldenPlec、Post-Punk.com

### 规则
- 每时段评分≥3的文章优先
- 每源最多1篇（避免单一源垄断）
- 历史1000条去重（MD5）
- 48小时内的文章
- 不碰CF站（NME、BrooklynVegan等⚠️标记的不加）

### 测试结果
- indie: ✅ 5篇（Aquarium Drunkard + The Quietus + Pitchfork + God Is in the TV + PopMatters）
- metal: ✅ 3篇（AMG + NCS + No Echo）
- folk: 待22:00自动触发

### 存储
- P项目：`tasks/pitchfork-expert/docs/`
- 英文原文：`en/{slot}/日期-源站-标题.md`
- 中英对照：`zh/{slot}/日期-源站-标题.md`

### 下一步
- 持续运行，积累翻译库
- 观察源站质量，必要时调整权重
- 未来可加非英语源（法语Les Inrockuptibles、意大利语等）
