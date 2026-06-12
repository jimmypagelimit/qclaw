## 任务背景
推进RYM Expert项目的发片日历能力，提取/new-music/页面新发片数据。

## 执行过程
1. 读取进度记录，选择发片日历作为推进目标
2. 分析/new-music/页面HTML结构
3. 迭代5版提取脚本，解决GBK编码、执行上下文销毁、正则匹配问题
4. 最终成功提取10条完整数据

## 关键结果
✅ 成功提取10条新发片数据，100%有评分
✅ 文件：rym-expert/explorations/2026-06-12-new-releases.md
✅ 数据：data/new-releases/new_music_v5.json
✅ 脚本：scripts/extract_new_releases_v5.py

## 结论建议
发片日历能力已稳定，支持后续翻页参数探索（>10条）和相似艺人能力推进。