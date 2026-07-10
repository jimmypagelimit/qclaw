import sqlite3

DB = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\_music_latest.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("SELECT album_id, artist, album_name, cover_image_url FROM albums WHERE album_id IN (566, 568, 596, 599, 600)")
for r in cur.fetchall():
    print('ID=%d | %s | %s | %s' % (r[0], r[1][:20], r[2][:20], r[3]))
conn.close()
