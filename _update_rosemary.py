# -*- coding: utf-8 -*-
import sqlite3
DB = r"C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\_music_latest.db"
conn = sqlite3.connect(DB)
cur = conn.cursor()

# 更新 duration 和 description
tracks = "1. Venus / Mascara | 2. Vestige | 3. Severine | 4. Hecate's Embrace | 5. Asteria | 6. Siofra | 7. In Dreams | 8. Madonna | 9. Endless, Dreamless"
cur.execute("""
    UPDATE albums SET duration=?, description=?
    WHERE album_id=551
""", ("26 min", tracks))

conn.commit()
cur.execute("SELECT album_id,album_name,artist,release_year,genre,duration,cover_image_url FROM albums WHERE album_id=551")
print(cur.fetchone())
conn.close()
print("完成")