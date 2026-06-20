import sqlite3

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("""SELECT album_id, album_name, artist, country,
                    (SELECT COUNT(*) FROM listen_history WHERE album_id=albums.album_id) as cnt
             FROM albums
             WHERE artist LIKE '%海朋森%' OR album_name LIKE '%成长小说%'""")
rows = c.fetchall()

print('找到专辑:')
for row in rows:
    print(f'  id={row["album_id"]}, {row["artist"]} - {row["album_name"]}, country={row["country"]}, 已听{row["cnt"]}次')

conn.close()
