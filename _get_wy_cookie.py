import sqlite3, os, json

# Chrome Cookie 数据库路径
chrome_path = os.path.expanduser(r'~AppData\Local\Google\Chrome\User Data\Default\Network\Cookies')
if not os.path.exists(chrome_path):
    chrome_path = os.path.expanduser(r'~AppData\Local\Google\Chrome\User Data\Default\Cookies')

print(f'Cookie DB: {chrome_path}')
print(f'Exists: {os.path.exists(chrome_path)}')

# 连接只读（避免锁文件）
conn = sqlite3.connect(f'file:{chrome_path}?mode=ro', uri=True)
cursor = conn.execute(
    "SELECT host_key, name, encrypted_value FROM cookies WHERE host_key LIKE '%163%' OR host_key LIKE '%netease%'"
)
rows = cursor.fetchall()
print(f'\nFound {len(rows)} 163 cookies:')
for row in rows:
    print(f'  {row[0]} | {row[1]} | encrypted_value_len={len(row[2])}')
conn.close()
