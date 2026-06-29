"""补全第10首 + 替换高清封面"""
import sqlite3, urllib.request, os

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
COVERS_DIR = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers'

conn = sqlite3.connect(DB)
cur = conn.cursor()

# 第10首
cur.execute(
    "INSERT INTO tracks (album_id, track_name, track_number, duration, source) "
    "VALUES (598, 'Fleur De Lis', 10, 293000, 'musicbrainz')"
)
conn.commit()
conn.close()
print('第10首已插入: Fleur De Lis')

# 高清封面 (Deezer 1000x1000)
cover_url = 'https://cdn-images.dzcdn.net/images/cover/b3a9dee0e68c75a03f059c563f664c83/1000x1000-000000-80-0-0.jpg'
cover_file = os.path.join(COVERS_DIR, '598-Ryan Beatty-Sweet Fortune.jpg')
try:
    urllib.request.urlretrieve(cover_url, cover_file)
    size = os.path.getsize(cover_file)
    print(f'高清封面已下载: {size//1024}KB')
except Exception as e:
    print(f'封面下载失败: {e}')
