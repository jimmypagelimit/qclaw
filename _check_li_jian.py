import sqlite3, sys
db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
c = conn.cursor()
c.execute("SELECT album_id, album_name, release_year FROM albums WHERE artist LIKE '%李健%' ORDER BY release_year")
rows = c.fetchall()
conn.close()
sys.stdout = open(1, 'w', encoding='utf-8', closefd=False)
for r in rows:
    print(f'{r[0]:3d} | {r[1]} | {r[2]}')
