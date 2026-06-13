## 任务背景
请求汇总本周（2026-06-07~06-13）多宗教RSS动态并通知飞书群。

## 执行过程
1. 并行抓取10个RSS源。
2. Jerusalem Post/Times of Israel/World Sikh News失败；SikhSiyasat停更于2020年。
3. 成功读取6个源内容并编译摘要。
4. 尝试发送飞书通知但被跨上下文限制阻止。

## 关键结果
- 佛教：Lion's Roar悲伤与无常修习、Tricycle慷慨（Dana）的治愈力
- 基督教：Bethany Christian Services LGBTQ政策大逆转、最高法院叫停氮气处决死囚牧师
- 伊斯兰教：Islam21c英国穆斯林政治参与系列
- 犹太教：Forward大卫·霍克尼去世
- 锡克教：无可用源
- 消息保存于religion-news_20260613.md，未能发送飞书

## 结论建议
摘要已生成并保存。需主agent在feishu上下文中手动发送通知至oc_85fa2f97d8d5d3b11eedad80146293e6。