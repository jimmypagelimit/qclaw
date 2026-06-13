import sqlite3, json
conn = sqlite3.connect(r"C:\Users\qujt\.qclaw\workspace\_music_latest.db")
c = conn.cursor()
c.execute("SELECT album_id, album_name, artist, cover_image_url FROM albums WHERE album_id = 458")
row = c.fetchone()
conn.close()
with open("_check458.json", "w", encoding="utf-8") as f:
    json.dump(row, f, ensure_ascii=False, indent=2)
