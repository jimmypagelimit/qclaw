#!/usr/bin/env python3
import sqlite3, json

DB = "G:/原创计划/music"
conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute("SELECT album_id, album_name, artist FROM albums WHERE cover_image_url IS NULL OR cover_image_url = ''")
rows = c.fetchall()
conn.close()

result = [{"id": r[0], "name": r[1], "artist": r[2]} for r in rows]
print(f"Missing: {len(result)}")
for r in result[:5]:
    print(f"  {r['artist']} - {r['name']}")