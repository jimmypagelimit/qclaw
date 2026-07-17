import urllib.request, json, sqlite3

# 确认 artist_id
db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute("SELECT artist_id, name FROM artists WHERE name='苏醒'")
row = cur.fetchone()
苏醒_artist_id = row[0] if row else None
conn.close()
print('苏醒 artist_id:', 苏醒_artist_id)

# 入库（不含 artist_id，看 API 返回什么 album_id）
album_data = {
    "album_name": "秋天",
    "artist": "苏醒",
    "release_year": 2007,
    "genre": "Hip-Hop/R&B",
    "description": "苏醒首张EP，2007年12月18日发行，天娱传媒。6首曲目：Preface、秋天、Happy Go、幸福曾经来过、分手的恋爱(+胡灵)、Happy Go (Remix)。",
    "release_company": "天娱传媒",
    "status": "active"
}

req = urllib.request.Request(
    'http://localhost:3456/api/albums',
    data=json.dumps(album_data).encode(),
    headers={'Content-Type': 'application/json'}
)
r = urllib.request.urlopen(req, timeout=15)
resp = json.loads(r.read())
print('Add result:', resp.get('success'))
album_id = resp.get('album', {}).get('album_id')
print('Album ID:', album_id)

# +1 listen
if album_id:
    req2 = urllib.request.Request(
        f'http://localhost:3456/api/albums/{album_id}/listen',
        data=json.dumps({'count': 1}).encode(),
        headers={'Content-Type': 'application/json'}
    )
    r2 = urllib.request.urlopen(req2, timeout=10)
    print('Listen +1:', json.loads(r2.read()).get('success'))
