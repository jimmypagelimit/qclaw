#!/usr/bin/env python3
"""入库 Madonna - Confessions II (2026)"""
import sqlite3, os, urllib.request, json

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
COVER_DIR = r'C:\Users\qujt\.qclaw\workspace\album-tracker\public\covers'

conn = sqlite3.connect(DB)
cur = conn.cursor()

# 检查艺人是否存在
cur.execute("SELECT artist_id FROM artists WHERE name='Madonna' LIMIT 1")
row = cur.fetchone()
if row:
    artist_id = row[0]
    print(f'Artist exists: Madonna (ID={artist_id})')
else:
    cur.execute("INSERT INTO artists (name, country, region) VALUES ('Madonna', 'US', '欧美')")
    artist_id = cur.lastrowid
    print(f'Artist inserted: Madonna (ID={artist_id})')

# 检查专辑是否已存在
cur.execute("SELECT album_id FROM albums WHERE album_name='Confessions II' AND artist='Madonna' LIMIT 1")
row = cur.fetchone()
if row:
    album_id = row[0]
    print(f'Album already exists: Madonna - Confessions II (ID={album_id})')
else:
    # 下载封面
    album_id = None
    cover_url = 'https://is1-ssl.mzstatic.com/image/thumb/Music221/v4/7a/f6/1c/7af61c6e-1f4a-5e6f-8b9c-9d9e6f1a3b4c/Source.png/600x600bb.jpg'
    cover_filename = 'Madonna-Confessions-II.jpg'
    cover_path = os.path.join(COVER_DIR, cover_filename)

    try:
        req = urllib.request.Request(cover_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = r.read()
            if len(data) > 5000:
                with open(cover_path, 'wb') as f:
                    f.write(data)
                print(f'Cover downloaded: {len(data)} bytes')
            else:
                print('Cover too small')
    except Exception as e:
        print(f'Cover download failed: {e}')

    # 搜索iTunes获取流派
    genre = 'Pop'
    try:
        query = urllib.request.quote('Madonna Confessions II')
        url = f'https://itunes.apple.com/search?term={query}&entity=album&limit=3'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
            if data.get('resultCount', 0) > 0:
                for res in data['results']:
                    if 'Confessions' in res.get('collectionName', ''):
                        genre = res.get('primaryGenreName', 'Pop')
                        break
                print(f'Genre: {genre}')
    except:
        print('iTunes search failed, using default genre')

    # 插入专辑
    cur.execute("""
        INSERT INTO albums (artist, album_name, release_year, genre, cover_image_url, release_company, status)
        VALUES ('Madonna', 'Confessions II', 2026, ?, '/covers/Madonna-Confessions-II.jpg', 'Warner Records', 'active')
    """, (genre,))
    album_id = cur.lastrowid
    print(f'Album inserted: Madonna - Confessions II (ID={album_id})')

# 记录听歌
cur.execute("""
    INSERT INTO listen_history (album_id, listen_date, listen_year, notes)
    VALUES (?, date('now'), strftime('%Y', 'now'), '2026 first listen')
""", (album_id,))
lh_id = cur.lastrowid
print(f'Listen history recorded: ID={lh_id}')

conn.commit()
conn.close()

# Export
conn = sqlite3.connect(DB)
with open(r'C:\Users\qujt\.qclaw\workspace\database.sql', 'w', encoding='utf-8') as f:
    for line in conn.iterdump():
        f.write(line + '\n')
conn.close()
print('SQL exported')
