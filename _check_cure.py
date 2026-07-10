import sqlite3

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.execute("SELECT album_id, album_name, release_year FROM albums WHERE artist LIKE '%Cure%' OR artist LIKE '%The Cure%'")
rows = cur.fetchall()

print(f'The Cure 专辑数: {len(rows)}')
for r in rows:
    print(f'  ID={r[0]} | {r[1]} ({r[2]})')

conn.close()
