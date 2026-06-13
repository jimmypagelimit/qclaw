## 任务背景
用户要求抓取16个宗教RSS源，筛选最近7天有价值文章，按类别汇总输出。

## 执行过程
1. Python脚本批量抓取16个RSS源（FEEDPARSER+REQUESTS）
2. 失败源通过web_fetch+FEEDPARSER重试/补救
3. 按佛教/基督教/伊斯兰教/犹太教/锡克教/综合分类整理
4. 限制每类≤3篇，写入Markdown报告

## 关键结果
- 成功抓取8/16源，获84篇有效文章
- 重点：Bethany禁止LGBTQ收养、美南浸信会修宪反女性牧师、FIFA世界杯允许Kirpan、纽约反犹仇恨犯罪激增150%
- 报告保存至religion_rss_report_2026-06-13.md

## 结论建议
数据采集完成，下周可优化JPost/Reddit等反爬源接入