# 深度翻译定时任务 - 建立完成

## 目标
从主力乐评/新闻网站定时抓取文章，逐段中英对照翻译，飞书推送

## 配置

### 三个时段
| 时间 | 时段 | 源站 | Cron ID |
|------|------|------|---------|
| 12:00 | 🎸 独立/摇滚 | Pitchfork + Stereogum + Consequence | bf8c27ad |
| 18:30 | 🔥 金属/极端 | Decibel + AMG + NCS + Metal Injection | 0fd3f61c |
| 22:00 | 🌊 民谣/前卫 | Aquarium Drunkard + The Quietus + TLOBF | 54b9c3f9 |

### 规则
- 每时段1-2篇（总计每天4-5篇）
- 翻译格式：逐段中英对照（英文原文→空行→第N段+中文翻译→空行）
- 选文标准：有趣重要就翻，高分优先，乐评+新闻+访谈
- 不翻文史
- 无重要更新不发

### 脚本
- `_deep_translate.py`：RSS抓取+评分筛选+全文提取
- 输出：`_translate_{slot}.json`（供cron agent读取翻译）
- 去重：`_translate_history.json`（MD5，最近500条）

### 测试结果
- indie slot: ✅ 抓取3篇（Lip Critic现场评+Pitchfork两篇乐评）
- metal/folk: 待18:30/22:00自动触发

### 飞书投递
- 目标：user:ou_830815046749687386321a76b269a7b5（张树私聊）
- 方式：cron announce → feishu channel
