# -*- coding: utf-8 -*-
"""入库: Porcelain Stars - Rosemary (2026)"""
import sqlite3, urllib.request, os

DB = r"C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\_music_latest.db"
COVER_DIR = r"C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers"
COVER_FILE = "porcelain-stars-rosemary.jpg"
COVER_URL = "https://i.scdn.co/image/ab67616d00001e02c9c9442eb09ff9c2b9162f419"
cover_path = os.path.join(COVER_DIR, COVER_FILE)
cover_url_val = "/covers/" + COVER_FILE

conn = sqlite3.connect(DB)
conn.execute("PRAGMA foreign_keys = ON")
cur = conn.cursor()

# 1. 查重
cur.execute("SELECT album_id FROM albums WHERE album_name='Rosemary' AND artist='Porcelain Stars'")
exist = cur.fetchone()
if exist:
    print("已存在: album_id=" + str(exist[0]))
    conn.close()
    exit(0)
print("不重复，准备入库")

# 2. 下载封面
os.makedirs(COVER_DIR, exist_ok=True)
try:
    req = urllib.request.Request(COVER_URL, headers={"User-Agent": "Mozilla/5.0"})
    cover_data = urllib.request.urlopen(req, timeout=10).read()
    with open(cover_path, 'wb') as f:
        f.write(cover_data)
    print("封面已下载: " + str(len(cover_data)) + " bytes")
except Exception as e:
    print("封面下载失败(可忽略): " + str(e))
    cover_url_val = None

# 3. 入库 albums
cur.execute("""
INSERT INTO albums (album_name, artist, release_year, genre, cover_image_url, first_listen_date, total_listen_count)
VALUES ('Rosemary', 'Porcelain Stars', 2026, 'Indie Folk', ?, '2026-01-31', 1)
""", (cover_url_val,))
album_id = cur.lastrowid
print("album_id: " + str(album_id))
conn.commit()

# 4. 入库 listen_history
cur.execute("""
INSERT INTO listen_history (album_id, listen_year, listen_date)
VALUES (?, 2026, '2026-01-31')
""", (album_id,))
lh_id = cur.lastrowid
print("listen_history id: " + str(lh_id))
conn.commit()

# 5. 验证
cur.execute("SELECT album_id,album_name,artist,release_year,genre,cover_image_url FROM albums WHERE album_id=?", (album_id,))
print("albums:", cur.fetchone())
cur.execute("SELECT * FROM listen_history WHERE album_id=?", (album_id,))
print("listen_history:", cur.fetchone())
conn.close()
print("完成")