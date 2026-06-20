import sqlite3

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
c = conn.cursor()

# 1. United Kingdom -> 英国
c.execute("SELECT album_id, album_name, artist FROM albums WHERE country='United Kingdom'")
print('United Kingdom 专辑:')
for row in c.fetchall():
    print(f'  id={row[0]}, {row[2]} - {row[1]}')
c.execute("UPDATE albums SET country='英国' WHERE country='United Kingdom'")
print(f'  -> 已更新为 英国')

# 2. Region=US -> NULL
c.execute("SELECT album_id, album_name, artist FROM albums WHERE region='US'")
print('Region=US 专辑:')
for row in c.fetchall():
    print(f'  id={row[0]}, {row[2]} - {row[1]}')
c.execute("UPDATE albums SET region=NULL WHERE region='US'")
print(f'  -> 已更新为 NULL')

conn.commit()
conn.close()
print('完成')
