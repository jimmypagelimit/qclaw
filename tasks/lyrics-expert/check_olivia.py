import sqlite3, urllib.request, json

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'

# 直接查数据库
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("""
    SELECT a.album_id, a.artist, a.album_name,
           (SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id) as pc
    FROM albums a
    WHERE a.album_name LIKE '%you seem pretty sad%'
""")
for row in cur.fetchall():
    print(f"DB: id={row[0]} artist={repr(row[1])} album={repr(row[2])} count={row[3]}")

# 查全部 listen_history 记录
cur.execute("""
    SELECT lh.album_id, a.artist, a.album_name, lh.listen_date
    FROM listen_history lh
    JOIN albums a ON lh.album_id = a.album_id
    WHERE a.album_name LIKE '%you seem pretty sad%'
    ORDER BY lh.listen_date
""")
for row in cur.fetchall():
    print(f"  {row[3]} - listen #{row[0]}")

conn.close()

# 查 API
print("\n--- API ---")
try:
    resp = urllib.request.urlopen("http://localhost:3456/api/stats", timeout=5)
    data = json.loads(resp.read())
    for item in data.get('topAlbums', []):
        if 'olivia' in item.get('artist', '').lower():
            print(f"API: {repr(item['artist'])} - {repr(item.get('album_name',''))}: {item.get('listen_count', 0)} plays")
except Exception as e:
    print(f"API error: {e}")
