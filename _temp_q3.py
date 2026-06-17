import sqlite3
db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute("SELECT album_id, album_name, artist, cover_image_url FROM albums WHERE album_name LIKE '%大只佬%' OR artist LIKE '%大只佬%'")
rows = cur.fetchall()
for r in rows:
    print(r)
if not rows:
    print("Not found by name, trying all...")
    cur.execute("SELECT album_id, album_name, artist FROM albums WHERE album_name LIKE '%V%'")
    for r in cur.fetchall():
        print(r)
conn.close()
