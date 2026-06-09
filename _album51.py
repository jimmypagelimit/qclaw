import sqlite3
db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
c = conn.cursor()
c.execute("SELECT album_name, artist, release_year, genre, style, country, region, duration, total_listen_count, cover_image_url, description FROM albums WHERE album_id = 51")
row = c.fetchone()
cols = ['album_name','artist','release_year','genre','style','country','region','duration','total_listen_count','cover_image_url','description']
for k,v in zip(cols, row):
    print(f'{k}: {v}')
conn.close()
