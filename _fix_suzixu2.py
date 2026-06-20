import sqlite3

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
c = conn.cursor()

c.execute("UPDATE albums SET country='中国', region='大陆' WHERE album_id=517")
conn.commit()

# verify
c.execute("SELECT album_name, artist, country, region FROM albums WHERE album_id=517")
row = c.fetchone()
with open(r'C:\Users\qujt\.qclaw\workspace\_verify_suzixu.txt', 'w', encoding='utf-8') as f:
    f.write(f'{row[1]} - {row[0]}: country={row[2]}, region={row[3]}\n')

conn.close()
print('Done')
