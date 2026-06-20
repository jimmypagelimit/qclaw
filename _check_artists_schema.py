import sqlite3

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
c = conn.cursor()

c.execute("PRAGMA table_info(artists)")
print('=== artists 表结构 ===')
for row in c.fetchall():
    print(f'  {row}')

c.execute("SELECT album_id, album_name, artist, country, region FROM albums WHERE country IS NOT NULL OR region IS NOT NULL LIMIT 5")
print('\n=== albums 有 country/region 的样本 ===')
for row in c.fetchall():
    print(f'  id={row[0]}, {row[1]} - {row[2]}: country={row[3]}, region={row[4]}')

conn.close()
