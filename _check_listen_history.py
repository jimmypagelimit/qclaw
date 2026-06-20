import sqlite3

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
c = conn.cursor()

c.execute("PRAGMA table_info(listen_history)")
print('listen_history 表结构:')
for row in c.fetchall():
    print(f'  {row}')

conn.close()
