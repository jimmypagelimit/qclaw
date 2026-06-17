import sqlite3
conn = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
cur = conn.cursor()
cur.execute("SELECT album_id, album_name, artist FROM albums WHERE artist LIKE '%施鑫文%' OR album_name LIKE '%巴蜀%'")
for r in cur.fetchall():
    print(repr(r))
conn.close()
