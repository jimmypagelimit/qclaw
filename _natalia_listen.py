import sqlite3
DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("""
    INSERT INTO listen_history (album_id, listen_date, listen_year, notes)
    VALUES (458, date('now'), strftime('%Y', 'now'), '2026 re-listen')
""")
lh_id = cur.lastrowid
conn.commit()
conn.close()
print('Listen added: ID=', lh_id)
