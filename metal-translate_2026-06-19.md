# 金属/硬核 深度翻译任务 | 2026-06-19

## 目标
执行 cron 任务：从 Metal Injection RSS 抓取近期金属/硬核新闻，深度翻译为中文，保存至 P 项目，发送飞书通知。

## 执行结果
✅ 成功完成

## 文章列表（6篇）

| # | 标题 | Slug | 类型 |
|---|------|------|------|
| 1 | LIMP BIZKIT 的 WES BORLAND 谈 SAM RIVERS 离世 | limp-bizkit-wes-borland-grieving-sam-rivers | 人物/哀悼 |
| 2 | 巨型 OZZY OSBOURNE 雕像在 Hellfest 亮相 | ozzy-osbourne-statue-hellfest | 音乐节/纪念 |
| 3 | WOLFGANG VAN HALEN 谈 Hawkins 致敬演出 | wolfgang-van-halen-taylor-hawkins-tribute | 人物/回忆 |
| 4 | ACID BATH 与 OBITUARY/THOU 纽约同台 | acid-bath-nyc-obituary-thou | 巡演 |
| 5 | DEP 《Calculating Infinity》25周年最终场次 | dillinger-escape-plan-calculating-infinity-25th | 巡演/纪念 |
| 6 | INSOMNIUM 新曲 Shadowlife | insomnium-shadowlife | 新发行 |

## 文件路径
- 英文原文：`tasks/pitchfork-expert/docs/en/metal/2026-06-19-metalinjection-*.md`
- 中英对照：`tasks/pitchfork-expert/docs/zh/metal/2026-06-19-metalinjection-*.md`

## 技术细节
- RSS 源：Metal Injection (`metalinjection.net/feed/`)
- RSS 直接 HTTP 抓取返回 403，改用 opencli + CDP 浏览器逐篇 extract
- 日期转换：UTC → CN (Asia/Shanghai)，`email.utils.parsedate_to_datetime`
- 翻译方式：人工逐段中英对照

## 飞书通知
lark-cli 安装失败（win32 平台不支持），消息内容已准备好但未能通过 CLI 发送。
需通过 feishu channel 直接回复。
