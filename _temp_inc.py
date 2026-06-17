import sqlite3, datetime, json
db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'

# 先停Web服务
import subprocess
import os

# 查端口3456
r = subprocess.run(['netstat', '-ano'], capture_output=True, text=True, shell=True)
for line in r.stdout.splitlines():
    if '3456' in line:
        print(f'PORT IN USE: {line.strip()}')
        
# 查进程
r2 = subprocess.run(['tasklist', '/fi', 'PID eq 1244'], capture_output=True, text=True, shell=True)
# 先不kill，直接操作数据库看看
conn = sqlite3.connect(db)
cur = conn.cursor()

# 先看有没有今天的记录
today = datetime.date.today().strftime('%Y-%m-%d')
cur.execute("SELECT id, listen_date FROM listen_history WHERE album_id = 555 ORDER BY listen_date DESC LIMIT 5")
print(f'TODAY: {today}')
print('Recent listens:', cur.fetchall())

conn.close()
