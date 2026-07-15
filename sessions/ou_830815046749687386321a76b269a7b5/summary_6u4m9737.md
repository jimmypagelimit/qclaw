## 任务背景
用户管理个人音乐收听数据库（A项目），涉及新专辑入库、收听记录更新及查询功能。用户反馈操作速度慢，要求优化入库流程。

## 执行过程
1. 分析慢的原因：每次入库都taskkill node进程（5-8秒/次）
2. 发现API支持POST /api/albums直接入库+收听
3. 识别sql.js内存缓存机制：首次写后需重启reload，之后批量API写入无需kill
4. 更新MEMORY.md和TOOLS.md记录新规则

## 关键结果
- 完成2张新专辑入库（BMTH、acloudyskye）
- 优化方案：写操作改用API，避免反复taskkill
- 规则固化：首次写前kill一次reload，之后批量写免kill
- 文件：C:\Users\qujt\.qclaw\workspace\MEMORY.md、TOOLS.md

## 结论建议
新流程已记录，后续入库统一走API。需补录两张专辑的收听记录及封面下载。