import shutil, json, pathlib

# C盘检查
usage = shutil.disk_usage("C:\\")
used_gb = usage.used / (1024**3)
free_gb = usage.free / (1024**3)
c_alert = used_gb > 60

# heartbeat-state.json
state_file = pathlib.Path("C:/Users/qujt/.qclaw/workspace/heartbeat-state.json")
state = {}
if state_file.exists():
    state = json.loads(state_file.read_text(encoding="utf-8"))

today = "2026-06-21"
now_ts = "2026-06-21 10:01"

print(f"c_used={used_gb:.1f}GB c_free={free_gb:.1f}GB c_alert={c_alert}")
print(f"last_c_check={state.get('lastChecks',{}).get('c_drive_check','从未')}")
print(f"last_weekly={state.get('lastChecks',{}).get('weekly_review','从未')}")
print(f"last_monthly={state.get('lastChecks',{}).get('monthly_review','从未')}")
