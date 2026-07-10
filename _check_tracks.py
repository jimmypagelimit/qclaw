import sqlite3, datetime

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()

# 看看tracks表结构
cur.execute('PRAGMA table_info(tracks)')
cols = [r[1] for r in cur.fetchall()]
print('tracks表字段:', cols)

conn.close()
