## 任务背景
用户发现音乐数据库查询与Web服务实际数据不一致，需要彻底解决数据库路径错误问题。
## 执行过程
1. 排查源码database.ts确认实际数据库路径
2. 比对本地与QEMU挂载盘的数据库文件
3. 发现昨天入库的3张专辑写错了位置
4. 修复数据到正确数据库文件
## 关键结果
- 正确数据库路径：`workspace/_music_latest.db`（非子目录副本）
- TOOLS.md已固化路径规则
- 补回3张专辑：Porcelain Stars、Greg Mendez、Feeble Little Horse
- Web服务正常（519张，1044条记录）
## 结论建议
问题已修复，后续查库需先看TOOLS.md确认路径。建议建立本地到QEMU盘的自动同步机制作为备份。