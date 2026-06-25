import sqlite3
db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

# 查所有含 Teens of Denial/Denial 的专辑
cur.execute("SELECT album_id, album_name, artist, release_year, cover_image_url FROM albums WHERE album_name LIKE '%Teens%' OR album_name LIKE '%Denial%'")
rows = cur.fetchall()
print('含Teens/Denial的专辑:')
for r in rows:
    print(f'  ID={r[0]}, name={r[1]}, artist={r[2]}, year={r[3]}, cover={r[4]}')

# 查listen_history
if rows:
    ids = [r[0] for r in rows]
    q = "SELECT id, album_id, listen_date, listen_year FROM listen_history WHERE album_id IN (%s)" % ','.join('?'*len(ids))
    cur.execute(q, ids)
    lh = cur.fetchall()
    print('\nlisten_history记录:')
    for r in lh:
        print(f'  id={r[0]}, album_id={r[1]}, date={r[2]}, year={r[3]}')

conn.close()
