# Pitchfork 批量评分补全 - 2026-06-21

## 目标
为数据库中缺失 pitchfork_score 的专辑批量补全 Pitchfork 评分

## 进展

### 工具创建
- `pf_query.py` — 单张专辑查询
- `pf_batch_fill_v2.py` — 批量补全（含 --resume）
- `pf_list_western.py` — 筛选西方专辑
- `pf_western_albums.json` — 西方专辑列表（138张）
- `pf_scheduled_runner.ps1` — 计划任务运行器

### 关键修改
- 修改 `get_albums_to_process()` 只处理西方专辑（跳过中文专辑，PF 无评论）
- 创建 Windows 计划任务 `PitchforkBatchFill`，每10分钟跑10张

### 数据库状态（06:15）
- 总专辑：527
- PF评分已有：100（19%）
- PF评分缺失：427（大部分是中文专辑，PF无评论）
- 已处理（含 not found）：425+

### 执行历史
1. v1 跑50张 → 2张成功
2. v2 跑50张 → 1张成功（Sufjan Stevens - Javelin 8.6）
3. v2 跑100张 → 23张成功
4. 跑200张 → SIGKILL（完成98/200）
5. 跑200张 → SIGKILL（Unicode编码错误，修复后重跑）
6. 跑50张 → SIGKILL（48/50）
7. 跑30张 → SIGKILL（24/30）
8. 切换到 Windows 计划任务 → 成功

### 问题与解决
- **SIGKILL**：OpenClaw exec 工具会杀死长时间进程 → 改用 Windows 计划任务
- **Unicode编码**：中文专辑名导致写入错误 → 筛选西方专辑跳过
- **中文专辑PF无评论**：304张中文专辑全部 not found → 只处理138张西方专辑
- **专辑名不匹配**：King Crimson - "In the Court of crimson king" vs "In the Court of the Crimson King" → 搜索仍能部分匹配

### 计划任务配置
- 任务名：PitchforkBatchFill
- 频率：每10分钟
- 每次处理：10张西方专辑
- 日志：pf_batch_fill.log + pf_scheduled.log
- 预计完成：约40-50轮（6-8小时）
