#!/usr/bin/env python3
"""入库 sueter7 - Todo Salio Bien en la Sencilla Villa Quien (2026)"""
import sqlite3, os, urllib.request, json, ssl

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
COVER_DIR = r'C:\Users\qujt\.qclaw\workspace\album-tracker\public\covers'

conn = sqlite3.connect(DB)
cur = conn.cursor()

# 检查艺人
cur.execute("SELECT artist_id FROM artists WHERE name='sueter7' LIMIT 1")
row = cur.fetchone()
if row:
    artist_id = row[0]
    print(f'Artist exists: sueter7 (ID={artist_id})')
else:
    cur.execute("INSERT INTO artists (name, country, region) VALUES ('sueter7', 'XX', '欧美')")
    artist_id = cur.lastrowid
    print(f'Artist inserted: sueter7 (ID={artist_id})')

# 检查专辑
cur.execute("SELECT album_id FROM albums WHERE album_name='Todo Salio Bien en la Sencilla Villa Quien' AND artist='sueter7' LIMIT 1")
row = cur.fetchone()
if row:
    album_id = row[0]
    print(f'Album exists: sueter7 - Todo Salio... (ID={album_id})')
else:
    # 下载封面
    cover_url = 'https://p1.music.126.net/iEvwlhNSVm7PwdnseTXUVQ==/109951173155579527.jpg'
    cover_filename = 'sueter7-TodoSalioBien.jpg'
    cover_path = os.path.join(COVER_DIR, cover_filename)
    
    ctx = ssl._create_unverified_context()
    try:
        req = urllib.request.Request(cover_url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://music.163.com'})
        with urllib.request.urlopen(req, timeout=15, context=ctx) as r:
            data = r.read()
            if len(data) > 5000:
                with open(cover_path, 'wb') as f:
                    f.write(data)
                print(f'Cover downloaded: {len(data)} bytes')
            else:
                print(f'Cover too small: {len(data)}')
    except Exception as e:
        print(f'Cover failed: {e}')

    # 插入专辑
    cur.execute("""
        INSERT INTO albums (artist, album_name, release_year, genre, cover_image_url, release_company, status)
        VALUES ('sueter7', 'Todo Salio Bien en la Sencilla Villa Quien', 2026, 'Indie Rock', '/covers/sueter7-TodoSalioBien.jpg', '1/4 Compania Discos', 'active')
    """)
    album_id = cur.lastrowid
    print(f'Album inserted: sueter7 - Todo Salio Bien... (ID={album_id})')

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
