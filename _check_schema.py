import sqlite3
db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
cols = [r[1] for r in conn.execute("PRAGMA table_info(albums)").fetchall()]
print('albums columns:', cols)
conn.close()
