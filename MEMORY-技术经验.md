# 技术经验（从 MEMORY.md 拆出）

## 浏览器绕过 Cloudflare（2026-04-23）
- OpenClaw 内置 browser 工具（Chromium）可以绕过 CF 保护
- Metal-Archives.com ✅（主页+乐队页），Genius ❌（ERR_ABORTED），AZLyrics ❌（超时）
- 浏览器不稳定时：stop 后重新 start 即可

## 文件写入规则
- 纯文本文件用 `qclaw-text-file` skill 的 `write_file.py` 脚本
- 临时文件（/tmp/）可用内置 write 工具
- 引号转义问题 → 用 temp_eval.js 文件方式传递 eval 代码

## Dify 相关
- Question 节点：暂停→存库→SSE 通知→resume API 恢复
- 不支持主动推送，需外部服务（飞书/企微 Bot）配合
- Discogs ✅ 和 MusicBrainz ✅ 均通过 browser 工具访问

## 乐评抓取经验（Courtney Barnett 实测 2026-04-13）

### Cloudflare 拦截情况
| 来源 | 状态 |
|------|------|
| **Pitchfork** | ✅ 稳定 |
| **Stereogum/NME** | ⚠️ 不稳定 |
| **The Guardian/DIY/Consequence/PopMatters/Paste** | ⚠️ 链接易变/404 |
| **The Quietus/Slant/BrooklynVegan/RYM/Metacritic** | ❌ 强 CF |

### 替代方案：AnyDecentMusic
- `anydecentmusic.com` 无 CF，50+ 乐评源加权平均分
- Courtney Barnett《Creature of Habit》7.5/10

### Cloudflare 绕过工具（未部署）
- FlareSolverr（Go）、cloudfire（Python+Playwright+Redis）
- Playwright 反检测：隐藏 webdriver、disable-blink-features=AutomationControlled
- **结论：优先用无 CF 源**

## album-review-compiler Skill
- 位置：`~/.qclaw/workspace/skills/album-review-compiler/SKILL.md`
- 策略：Pitchfork → Stereogum → NME → 其他无 CF 源

## 木马乐队资料（2026-04-18）
- 全名：木马乐队 (Muma)，主唱木玛（谢强），1998年湖南株洲
- 后朋克+暗黑美学，受 Joy Division/Led Zeppelin 影响
- **7张专辑三阶段**：
  1. 木马乐队：《木马》(2000, 8.7) → 《Yellow Star》(2003, EP) → 《果冻帝国》(2004)
  2. 木玛&Third Party：《丝绒公路》(2007) → 《进化》(2011)
  3. 重组：《洗心革面》(2019, LIVE) → 《忘忧神丹》(2021)
- 《后来》改编（乐夏2, 2020）：少女心事→少年故事，风笛+失真吉他+大合唱，29票晋级十强

## 独立音乐 RSS
- 每天检查 Pitchfork/Stereogum/Metal Injection 等
- 完整源列表见 `RSS-SOURCES.md`
- 重要新闻飞书推送
