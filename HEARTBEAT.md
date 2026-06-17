# HEARTBEAT.md

# 定期任务检查清单

> **投递目标**：所有 heartbeat 提醒统一发到本群 `oc_85fa2f97d8d5d3b11eedad80146293e6`

## 🪞 输出质量反思（每日）

- 每日首次 heartbeat 回顾昨日输出，自检：
  - 有无过程堆砌？（搜索过程该省就省）
  - 有无信息轰炸？（视觉层次清晰吗）
  - 有无过度解读？（没问的别主动加）
  - 有无废话？（"让我试试"之类的删掉）
- 发现问题→记入 memory，下次改进

---

## 💿 ~~荒岛唱片每日同步~~（已废弃，用户要求彻底忘记）

## 📋 每日工作总结与推送（~17:00）

- 每日约17:00 heartbeat 时执行
- 汇总当日完成的工作（memory/2026-MM-DD.md + git diff）
- commit + push workspace 仓库
- 飞书通知：当日工作摘要 + 推送状态
- 无需用户提醒，主动执行

## 💾 C盘空间监控（每天）

- **阈值**：C 盘已用空间 > 60GB 时飞书告警
- **检查频率**：每日首次 heartbeat
- **检查方法**：Python `shutil.disk_usage("C:\\")`
- **告警格式**：⚠️ C盘占用告警 | 当前已用：XX.X GB | 当前剩余：XX.X GB
- **正常时不发通知**（避免骚扰）
- **heartbeat-state.json 追踪**：记录 `lastChecks.c_drive_check`

### Python 检查代码（用于 heartbeat）
```python
import shutil
usage = shutil.disk_usage("C:\\") 
used_gb = usage.used / (1024**3)
free_gb = usage.free / (1024**3)
if used_gb > 60:
    print(f"⚠️ C盘占用告警 | 当前已用：{used_gb:.1f} GB | 当前剩余：{free_gb:.1f} GB")
```

## 🌿 身心保养提醒

- **周日身心回顾（20:00-21:30）**：花3分钟回顾本周身心状态
- **每月1号月度评估（9:00-11:00）**：回顾上月整体状态
- 同一条提醒每天只发一次，深夜（23:00-7:00）不打扰

### heartbeat-state.json 追踪
```json
{
  "lastChecks": {
    "weekly_review": "2026-06-08",
    "monthly_review": "2026-05-01",
    "c_drive_check": "2026-06-08"
  }
}
```

