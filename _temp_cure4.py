import urllib.request, sqlite3, os

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
COVERS = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers'
HEADERS = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://music.163.com/'}

pic_url = 'http://p2.music.126.net/yn3ddBzL6LAu-bKchXuSwg==/109951173226721551.jpg'
dest = os.path.join(COVERS, '325-The Cure-The Cure.jpg')

req = urllib.request.Request(pic_url, headers=HEADERS)
data = urllib.request.urlopen(req, timeout=10).read()
with open(dest, 'wb') as f:
    f.write(data)
print(f'Downloaded {len(data)} bytes')

# DB already has correct path, no need to update
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("SELECT album_id, cover_image_url FROM albums WHERE album_id=325")
r = cur.fetchone()
print(f'DB: album_id={r[0]} cover={r[1]}')
conn.close()
