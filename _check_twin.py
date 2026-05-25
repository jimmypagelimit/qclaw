import sqlite3
db = r'G:\原创计划\music'
conn = sqlite3.connect(db)
c = conn.cursor()
c.execute('SELECT album_id, album_name, artist, release_year, cover_image_url FROM albums WHERE artist LIKE "%Car Seat Headrest%" AND album_name LIKE "%Twin Fantasy%"')
for r in c.fetchall():
    print(r)
conn.close()