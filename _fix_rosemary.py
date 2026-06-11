# -*- coding: utf-8 -*-
"""更新 Porcelain Stars - Rosemary 封面 + 风格"""
import sqlite3, urllib.request, os

DB = r"C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\_music_latest.db"
COVER_DIR = r"C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers"
COVER_FILE = "porcelain-stars-rosemary.jpg"
COVER_URL = "https://is1-ssl.mzstatic.com/image/thumb/Music211/v4/5d/bb/91/5dbb914e-39d5-40aa-5742-b18c21174db8/artwork.jpg/600x600bb.jpg"

conn = sqlite3.connect(DB)
cur = conn.cursor()

# 1. 确认 album_id
cur.execute("SELECT album_id,genre FROM albums WHERE album_name='Rosemary' AND artist='Porcelain Stars'")
row = cur.fetchone()
if not row:
    print("未找到 Rosemary by Porcelain Stars")
    conn.close()
    exit(1)
album_id = row[0]
print("album_id:", album_id, "| 当前 genre:", row[1])

# 2. 下载封面
os.makedirs(COVER_DIR, exist_ok=True)
try:
    req = urllib.request.Request(COVER_URL, headers={"User-Agent": "Mozilla/5.0"})
    cover_data = urllib.request.urlopen(req, timeout=10).read()
    cover_path = os.path.join(COVER_DIR, COVER_FILE)
    with open(cover_path, 'wb') as f:
        f.write(cover_data)
    print("封面下载成功: " + str(len(cover_data)) + " bytes")
    cover_url_val = "/covers/" + COVER_FILE
except Exception as e:
    print("封面下载失败: " + str(e))
    cover_url_val = None

# 3. 更新 albums 表
if cover_url_val:
    cur.execute("""
        UPDATE albums SET genre='Alternative', cover_image_url=?
        WHERE album_id=?
    """, (cover_url_val, album_id))
else:
    cur.execute("""
        UPDATE albums SET genre='Alternative'
        WHERE album_id=?
    """, (album_id,))

conn.commit()

# 4. 验证
cur.execute("SELECT album_id,album_name,artist,release_year,genre,cover_image_url FROM albums WHERE album_id=?", (album_id,))
print("更新后:", cur.fetchone())
conn.close()
print("完成")