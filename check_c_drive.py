import shutil

usage = shutil.disk_usage('C:\\')
used_gb = usage.used / (1024**3)
free_gb = usage.free / (1024**3)

print(f'C: Used: {used_gb:.1f} GB')
print(f'C: Free: {free_gb:.1f} GB')
print(f'Threshold: 50 GB')

if used_gb > 50:
    print(f'WARNING: C: drive usage exceeds threshold! Used: {used_gb:.1f} GB')
else:
    print('OK: C: drive usage is normal')
