#!/usr/bin/env python3
"""入库 Nando García - Lover Man (2026)"""
import sqlite3, os, urllib.request, json

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
COVER_DIR = r'C:\Users\qujt\.qclaw\workspace\album-tracker\public\covers'

conn = sqlite3.connect(DB)
cur = conn.cursor()

# 检查艺人
cur.execute("SELECT artist_id FROM artists WHERE name='Nando Garcia' LIMIT 1")
row = cur.fetchone()
if row:
    artist_id = row[0]
    print(f'Artist exists: Nando Garcia (ID={artist_id})')
else:
    cur.execute("INSERT INTO artists (name, country, region) VALUES ('Nando Garcia', 'XX', '欧美')")
    artist_id = cur.lastrowid
    print(f'Artist inserted: Nando Garcia (ID={artist_id})')

# 检查专辑
cur.execute("SELECT album_id FROM albums WHERE album_name='Lover Man' AND artist='Nando Garcia' LIMIT 1")
row = cur.fetchone()
if row:
    album_id = row[0]
    print(f'Album exists: Nando Garcia - Lover Man (ID={album_id})')
    # 下载封面
    cover_url = 'https://is1-ssl.mzstatic.com/image/thumb/Music221/v4/75/63/c3/7563c3bd-0c0a-c8bb-89ad-ecaf8b58d5e3/820200603661.jpg/600x600bb.jpg'
    cover_path = os.path.join(COVER_DIR, f'{album_id}-NandoGarcia-LoverMan.jpg')
    try:
        req = urllib.request.Request(cover_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = r.read()
            if len(data) > 5000:
                with open(cover_path, 'wb') as f:
                    f.write(data)
                print(f'Cover downloaded: {len(data)} bytes')
                cur.execute(f"UPDATE albums SET cover_image_url='/covers/{album_id}-NandoGarcia-LoverMan.jpg' WHERE album_id=?", (album_id,))
                print('DB cover updated')
    except Exception as e:
        print(f'Cover failed: {e}')
else:
    # 下载封面
    cover_url = 'https://is1-ssl.mzstatic.com/image/thumb/Music221/v4/75/63/c3/7563c3bd-0c0a-c8bb-89ad-ecaf8b58d5e3/820200603661.jpg/600x600bb.jpg'
    cover_filename = 'NandoGarcia-LoverMan.jpg'
    cover_path = os.path.join(COVER_DIR, cover_filename)
    try:
        req = urllib.request.Request(cover_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = r.read()
            if len(data) > 5000:
                with open(cover_path, 'wb') as f:
                    f.write(data)
                print(f'Cover downloaded: {len(data)} bytes')
    except Exception as e:
        print(f'Cover failed: {e}')

    # 插入专辑
    cur.execute("""
        INSERT INTO albums (artist, album_name, release_year, genre, cover_image_url, release_company, status)
        VALUES ('Nando Garcia', 'Lover Man', 2026, 'Alternative', '/covers/NandoGarcia-LoverMan.jpg', 'Independent', 'active')
    """)
    album_id = cur.lastrowid
    print(f'Album inserted: Nando Garcia - Lover Man (ID={album_id})')

# 记录听歌
cur.execute("""
    INSERT INTO listen_history (album_id, listen_date, listen_year, notes)
    VALUES (?, date('now'), strftime('%Y', 'now'), '2026 first listen')
""", (album_id,))
lh_id = cur.lastrowid
print(f'Listen history: ID={lh_id}')

conn.commit()
conn.close()

# Export
conn = sqlite3.connect(DB)
with open(r'C:\Users\qujt\.qclaw\workspace\database.sql', 'w', encoding='utf-8') as f:
    for line in conn.iterdump():
        f.write(line + '\n')
conn.close()
print('SQL exported')
