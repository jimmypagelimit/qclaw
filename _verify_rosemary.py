# -*- coding: utf-8 -*-
import sqlite3
DB = r"C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\_music_latest.db"
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("SELECT album_id,album_name,artist,release_year,genre FROM albums WHERE album_name='Rosemary'")
print(cur.fetchone())
cur.execute("SELECT * FROM listen_history WHERE album_id=551")
print(cur.fetchall())
conn.close()