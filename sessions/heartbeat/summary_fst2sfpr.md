## 任务背景
处理 album-tracker 封面下载定时任务的执行失败问题。

## 执行过程
1. 分析任务失败原因
2. 检查 G 盘可访问性
3. 修复脚本语法并记录

## 关键结果
- 发现两个问题：PowerShell 5.1 不支持 `&&` 运算符，G 盘虽映射但实际不可访问
- 更新 heartbeat-state.json 将 g_drive_mounted 设为 false
- 后续 heartbeat 将跳过封面下载直到 G 盘恢复

## 结论建议
封面下载任务因 G 盘不可访问被跳过，建议下次 heartbeat 重新检查 G 盘状态。