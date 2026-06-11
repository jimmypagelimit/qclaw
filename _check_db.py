# -*- coding: utf-8 -*-
import sqlite3
p = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\_music_latest.db'
conn = sqlite3.connect(p)
tables = [t[0] for t in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print("Tables:", tables)
# Check columns of albums
cols = [d[1] for d in conn.execute("PRAGMA table_info(albums)").fetchall()]
print("Albums columns:", cols)
conn.close()