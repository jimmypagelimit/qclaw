import urllib.request, os

artwork = 'https://is1-ssl.mzstatic.com/image/thumb/Music128/v4/dd/3f/56/dd3f566c-be5d-a268-af0e-75f85e868609/4711479222447.jpg/500x500bb.jpg'
cover_path = r'C:\Users\qujt\.qclaw\workspace\album-tracker\public\covers\558-Tizzy_Bac-SummerHeat.jpg'

req = urllib.request.Request(artwork, headers={'User-Agent': 'Mozilla/5.0'})
resp = urllib.request.urlopen(req, timeout=10)
data = resp.read()
with open(cover_path, 'wb') as f:
    f.write(data)
size = os.path.getsize(cover_path)
print(f"Cover saved: {size} bytes")

import sqlite3
DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("UPDATE albums SET cover_image_url = ? WHERE album_id = ?", ('/covers/558-Tizzy_Bac-SummerHeat.jpg', 558))
conn.commit()
conn.close()
print("DB cover_url updated to /covers/558-Tizzy_Bac-SummerHeat.jpg")
