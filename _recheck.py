# -*- coding: utf-8 -*-
import sqlite3
DB = r"C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\_music_latest.db"
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("SELECT album_id,album_name,artist FROM albums WHERE album_name='Rosemary'")
print(cur.fetchone())
conn.close()