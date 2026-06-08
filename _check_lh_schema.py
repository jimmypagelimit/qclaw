import sqlite3
conn = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
cur = conn.cursor()
cur.execute("PRAGMA table_info(listen_history)")
cols = [r[1] for r in cur.fetchall()]
print('listen_history columns:', cols)
conn.close()
