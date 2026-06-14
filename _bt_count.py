import sqlite3

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.execute("SELECT album_id, album_name, release_year, genre FROM albums WHERE artist_id = 21 ORDER BY release_year")
rows = cur.fetchall()
print(f"Big Thief 专辑数: {len(rows)}")
for r in rows:
    print(f"  id={r[0]} | {r[1]} | {r[2]} | {r[3][:50]}")

conn.close()
