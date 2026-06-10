## 任务背景
用户请求从 rateyourmusic.com 爬取 Rock 风格的子风格树形图。

## 执行过程
1. 使用 CloakBrowser headless=False 绕过 Cloudflare 保护
2. 尝试访问 /genre/ 首页失败，改为直接访问 /genre/rock/ 单流派页面
3. 通过 window.location.href 导航 + 25-30秒等待通过 CF challenge
4. 提取 81 个 Rock 子流派并整理为 9 大分支
5. 用户确认后，将抓取方法写入 TOOLS.md 和 MEMORY.md 长期记忆

## 关键结果
- 成功获取 RYM Rock 完整子流派列表（81个）
- 整理为结构化 JSON 和树形图
- 抓取方法已永久记录：CloakBrowser + /genre/{slug}/ + 链接文本提取

## 结论建议
RYM 风格分支抓取方案已验证有效，下次可直接复用。可继续扩展抓取 Metal、Punk 等其他顶级流派。