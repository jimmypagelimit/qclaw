import sqlite3
conn = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
cur = conn.cursor()
for tbl in ['albums_2024','albums_2025','albums_2026']:
    cur.execute(f"PRAGMA table_info({tbl})")
    cols = [r[1] for r in cur.fetchall()]
    print(tbl, 'columns:', cols)
conn.close()
