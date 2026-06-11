import sqlite3
db = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\_music_latest.db'
conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute("SELECT album_id, album_name, artist, release_year FROM albums WHERE album_name LIKE '%Beauty%' OR artist LIKE '%Greg%'")
rows = cur.fetchall()
for r in rows:
    print(r)
conn.close()
if not rows:
    print("NOT FOUND - needs insertion")
