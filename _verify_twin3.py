import sqlite3, urllib.request, json

# 先查 API
url = 'http://localhost:3456/api/albums?year=2026&search=Twin'
try:
    r = json.loads(urllib.request.urlopen(url).read())
    print('API result:', r.get('albums', []))
except Exception as e:
    print('API error:', e)

# 直接查 DB
conn = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
cur = conn.cursor()
cur.execute("SELECT album_id, album_name, artist, total_listen_count FROM albums WHERE album_name LIKE '%Twin%'")
row = cur.fetchone()
if row:
    album_id = row[0]
    print(f"\nDB: id={album_id}, {row[1]} - {row[2]}, total={row[3]}")
    cur.execute("SELECT COUNT(*) FROM listen_history WHERE album_id=? AND listen_year=2026", (album_id,))
    cnt_2026 = cur.fetchone()[0]
    print(f"2026 listens: {cnt_2026}")
conn.close()
