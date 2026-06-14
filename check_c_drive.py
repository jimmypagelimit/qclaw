import shutil

usage = shutil.disk_usage('C:\\')
used_gb = usage.used / (1024**3)
free_gb = usage.free / (1024**3)

print(f'C盘已用: {used_gb:.1f} GB')
print(f'C盘剩余: {free_gb:.1f} GB')

if used_gb > 50:
    print('C盘占用告警 | 当前已用：{:.1f} GB | 当前剩余：{:.1f} GB'.format(used_gb, free_gb))
else:
    print('C盘空间正常')
