import sqlite3
from datetime import date

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
c = conn.cursor()

# 查 listen_history 表结构
c.execute("PRAGMA table_info(listen_history)")
print("listen_history schema:")
for row in c.fetchall():
    print(row)

# 查 Olivia 专辑
c.execute("SELECT album_id, album_name, artist FROM albums WHERE artist LIKE '%Olivia%' OR album_name LIKE '%Olivia%'")
rows = c.fetchall()
print("\nOlivia albums:", rows)

conn.close()
