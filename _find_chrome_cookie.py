import sqlite3, os

# 尝试多个可能的 Chrome Cookie 路径
paths = [
    os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data\Default\Network\Cookies'),
    os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data\Default\Cookies'),
    os.path.expandvars(r'%APPDATA%\..\Local\Google\Chrome\User Data\Default\Network\Cookies'),
    r'C:\Users\qujt\AppData\Local\Google\Chrome\User Data\Default\Network\Cookies',
    r'C:\Users\qujt\AppData\Local\Google\Chrome\User Data\Default\Cookies',
]

for p in paths:
    exists = os.path.exists(p)
    size = os.path.getsize(p) if exists else 0
    print(f'{"OK" if exists else "NO"} {size:>12} bytes  {p}')

# 搜索 Network 目录
nd = r'C:\Users\qujt\AppData\Local\Google\Chrome\User Data'
if os.path.exists(nd):
    for root, dirs, files in os.walk(nd):
        for f in files:
            if 'ookie' in f:
                full = os.path.join(root, f)
                print(f'  Found: {full} ({os.path.getsize(full)} bytes)')
