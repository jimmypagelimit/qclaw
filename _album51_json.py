import sqlite3, json
db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
c = conn.cursor()
c.execute("SELECT album_name, artist, release_year, genre, style, country, region, duration, total_listen_count, cover_image_url, description FROM albums WHERE album_id = 51")
row = c.fetchone()
cols = ['album_name','artist','release_year','genre','style','country','region','duration','total_listen_count','cover_image_url','description']
data = {k: v for k, v in zip(cols, row)}
with open(r'C:\Users\qujt\.qclaw\workspace\_album51.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print("done")
conn.close()
