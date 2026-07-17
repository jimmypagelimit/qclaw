import urllib.request, json, sqlite3

# 先查 ID=611 的 listen_history
db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute("SELECT id, album_id, listen_date FROM listen_history WHERE album_id=611 ORDER BY id")
rows = cur.fetchall()
print(f'Listen records for album 611: {len(rows)}')
for r in rows:
    print(f'  id={r[0]}, date={r[2]}')
conn.close()
