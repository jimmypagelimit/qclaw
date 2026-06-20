import sqlite3
import os

db = 'C:/Users/qujt/.qclaw/workspace/_music_latest.db'
covers_dir = 'C:/Users/qujt/.qclaw/workspace/tasks/2026-05-12-long-term-project/album-tracker/public/covers'

conn = sqlite3.connect(db)
c = conn.cursor()

c.execute("SELECT COUNT(*) FROM albums WHERE release_mbid IS NOT NULL AND release_mbid != ''")
total_mbid = c.fetchone()[0]

c.execute("SELECT COUNT(*) FROM albums WHERE cover_image_url IS NOT NULL AND cover_image_url != ''")
has_cover = c.fetchone()[0]

conn.close()

if os.path.exists(covers_dir):
    files = [f for f in os.listdir(covers_dir) if f.endswith('.jpg')]
    print(f"covers 目录实际文件数: {len(files)}")
else:
    print("covers 目录不存在")

print(f"有 MBID 的专辑数: {total_mbid}")
print(f"已有 cover_image_url 的专辑数: {has_cover}")
