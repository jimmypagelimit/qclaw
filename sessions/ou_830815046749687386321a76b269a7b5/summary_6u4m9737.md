## 任务背景
用户反馈"木马"等专辑封面显示空白，需排查并修复。

## 执行过程
1. 排查发现sql.js内存数据库缓存问题，修改DB文件后需kill所有node进程+释放端口+重启
2. 验证HTTP API返回路径正确性，确认图片文件内容有效
3. 完成Itinerary单引号Bug批量修复及艺人排行榜Bug修复

## 关键结果
- 木马、Itinerary、Pluto三张专辑封面成功显示
- 12个含单引号的封面文件批量重命名
- 艺人排行榜"0次"Bug修复（`renderArtistLeaderboard`函数）
- 修复记录写入`2026-06-23-cover-fix.md`及`memory/2026-06-23.md`

## 结论建议
sql.js项目改DB后必须kill进程+释放端口+重启，仅restart不够。今日所有临时脚本已清理。