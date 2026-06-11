# -*- coding: utf-8 -*-
"""用 Discogs 数据更新 Porcelain Stars - Rosemary"""
import sqlite3, urllib.request, os, re

DB = r"C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\_music_latest.db"
COVER_DIR = r"C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers"
COVER_FILE = "porcelain-stars-rosemary.jpg"
DISCOGS_COVER = "https://i.discogs.com/LW1vad62-bB4eQs_FRg-b8OzTY5zolZU2al9CcStOlc/rs:fit/g:sm/q:90/h:508/w:600/czM6Ly9kaXNjb2dz/LWRhdGFiYXNlLWlt/YWdlcy9SLTM3MDIx/MTk3LTE3NzU3NjAx/NzMtMTAxOC5qcGVn.jpeg"

conn = sqlite3.connect(DB)
cur = conn.cursor()

# 1. 下载 Discogs 封面
os.makedirs(COVER_DIR, exist_ok=True)
cover_path = os.path.join(COVER_DIR, COVER_FILE)
try:
    req = urllib.request.Request(DISCOGS_COVER, headers={"User-Agent": "Mozilla/5.0"})
    data = urllib.request.urlopen(req, timeout=10).read()
    with open(cover_path, 'wb') as f:
        f.write(data)
    print("Discogs 封面下载成功: " + str(len(data)) + " bytes")
    cover_ok = True
except Exception as e:
    print("Discogs 封面下载失败: " + str(e))
    cover_ok = False

# 2. 更新专辑信息
# Discogs 风格: Emo, Blackgaze, Baroque Pop
# 精确曲目时长
tracks_detail = "1. Venus / Mascara (3:33) | 2. Vestige (3:53) | 3. Severine (3:14) | 4. Hecate's Embrace (2:05) | 5. Asteria (3:28) | 6. Siofra (3:30) | 7. In Dreams (3:24) | 8. Madonna (1:55) | 9. Endless, Dreamless (5:21)"
duration_sec = 33+53+14+5+28+30+24+55+321  # 5:21 = 321s
duration_str = "31 min"

cur.execute("""
    UPDATE albums SET
        genre='Rock/Pop',
        style='Emo, Blackgaze, Baroque Pop',
        duration=?,
        description=?,
        cover_image_url=?
    WHERE album_id=551
""", (duration_str, tracks_detail, "/covers/" + COVER_FILE if cover_ok else None))

conn.commit()

# 3. 验证
cur.execute("SELECT album_id,album_name,artist,genre,style,duration,cover_image_url FROM albums WHERE album_id=551")
print("\n更新后:", cur.fetchone())

# 4. 更新 listen_history 的 notes 字段（记下来源）
cur.execute("UPDATE listen_history SET notes='iTunes+Discogs' WHERE album_id=551")
conn.commit()
print("listen_history notes 已更新")

conn.close()
print("完成")