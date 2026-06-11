import shutil
import datetime

usage = shutil.disk_usage('C:\\')
used_gb = usage.used / (1024**3)
free_gb = usage.free / (1024**3)

print(f'C: 已用 {used_gb:.1f} GB | 剩余 {free_gb:.1f} GB')
current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(f'检查时间: {current_time}')

if used_gb > 50:
    print(f'⚠️ C盘占用告警 | 当前已用：{used_gb:.1f} GB | 当前剩余：{free_gb:.1f} GB')
else:
    print('C盘空间正常')
