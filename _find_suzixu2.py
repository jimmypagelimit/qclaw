import sqlite3

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
conn.row_factory = sqlite3.Row
c = conn.cursor()

c.execute("SELECT album_id, album_name, artist, country, region FROM albums WHERE artist LIKE '%苏紫旭%'")
rows = c.fetchall()

with open(r'C:\Users\qujt\.qclaw\workspace\_find_suzixu.txt', 'w', encoding='utf-8') as f:
    for row in rows:
        f.write(f'id={row["album_id"]}, {row["artist"]} - {row["album_name"]}: country={row["country"]}, region={row["region"]}\n')

conn.close()
print('Done')
