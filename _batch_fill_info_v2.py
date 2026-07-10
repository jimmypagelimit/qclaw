#!/usr/bin/env python3
"""批量补全专辑基本信息：封面+发行公司+流派"""
import sqlite3, os, urllib.request, json, time

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
COVER_DIR = r'C:\Users\qujt\.qclaw\workspace\album-tracker\public\covers'

def ascii_safe(s):
    if s:
        return s.encode('ascii', 'ignore').decode('ascii').strip()
    return ''

def safe_filename(s):
    return "".join(c for c in s if c not in r'\/:*?"<>|').strip()

def download_cover(url, path):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = r.read()
            if len(data) > 5000:
                with open(path, 'wb') as f:
                    f.write(data)
                return len(data)
    except:
        pass
    return 0

def itunes_search(artist, album):
    query = urllib.request.quote(f'{artist} {album}'.replace(' ', '+'))
    url = f'https://itunes.apple.com/search?term={query}&entity=album&limit=5'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
            if data.get('resultCount', 0) > 0:
                for res in data['results']:
                    res_name = res.get('collectionName', '').lower()
                    res_artist = res.get('artistName', '').lower()
                    album_lower = album.lower()
                    artist_lower = artist.lower()
                    if album_lower in res_name or artist_lower in res_artist:
                        artwork = res.get('artworkUrl100', '').replace('100x100', '600x600')
                        return {
                            'cover_url': artwork,
                            'company': res.get('copyright', ''),
                            'genre': res.get('primaryGenreName', ''),
                        }
                res = data['results'][0]
                artwork = res.get('artworkUrl100', '').replace('100x100', '600x600')
                return {
                    'cover_url': artwork,
                    'company': res.get('copyright', ''),
                    'genre': res.get('primaryGenreName', ''),
                }
    except:
        pass
    return None

# 专辑列表
albums = [
    {'id': 602, 'artist': 'The Microphones', 'album': 'The Glow, Pt. 2', 'year': 2001, 'genre': 'Indie Rock'},
    {'id': 601, 'artist': 'The Cure', 'album': 'Songs of a Lost World', 'year': 2024, 'genre': 'Post-Punk'},
    {'id': 599, 'artist': 'Suimeng Feiyue', 'album': 'Outside Is Summer', 'year': 2026, 'genre': 'Indie Rock'},
    {'id': 598, 'artist': 'Ryan Beatty', 'album': 'Sweet Fortune', 'year': 2026, 'genre': 'R&B'},
    {'id': 597, 'artist': 'At The Gates', 'album': 'The Ghost of a Future Dead', 'year': 2026, 'genre': 'Melodic Death Metal'},
    {'id': 596, 'artist': 'Zheng Yuan', 'album': 'Brush Shoulder', 'year': 2008, 'genre': 'Mandopop'},
    {'id': 595, 'artist': 'Fires in the Distance', 'album': 'Circadian Promise', 'year': 2026, 'genre': 'Post-Metal'},
    {'id': 594, 'artist': 'Warning', 'album': 'Rituals of Shame', 'year': 2026, 'genre': 'Doom Metal'},
    {'id': 593, 'artist': 'Pixies', 'album': 'Doolittle', 'year': 1989, 'genre': 'Alternative Rock'},
]

conn = sqlite3.connect(DB)
cur = conn.cursor()

print('=== Batch Fill Album Info ===')

for a in albums:
    album_id = a['id']
    artist = a['artist']
    album_name = a['album']
    year = a['year']
    default_genre = a['genre']

    print(f'\n--- {ascii_safe(artist)} - {ascii_safe(album_name)} (ID={album_id}) ---')

    cur.execute('SELECT cover_image_url, release_company, genre FROM albums WHERE album_id=?', (album_id,))
    row = cur.fetchone()
    current_cover, current_company, current_genre = row

    needs_update = {}
    info = None
    new_cover_path = None

    # 1. 缺封面
    if not current_cover:
        print('  Cover: MISSING, searching iTunes...')
        info = itunes_search(artist, album_name)
        if info and info['cover_url']:
            cover_filename = f'{album_id}-{safe_filename(artist)}-{safe_filename(album_name)}.jpg'
            cover_path = os.path.join(COVER_DIR, cover_filename)
            size = download_cover(info['cover_url'], cover_path)
            if size > 0:
                needs_update['cover_image_url'] = f'/covers/{cover_filename}'
                print(f'  Cover: OK ({size} bytes)')
                new_cover_path = cover_path
            else:
                print('  Cover: FAILED')
        else:
            print('  Cover: NOT FOUND on iTunes')
    else:
        print(f'  Cover: already set')

    # 2. 缺发行公司
    if not current_company:
        if not info:
            info = itunes_search(artist, album_name)
        if info and info['company']:
            # 从copyright提取公司名 (通常是 "(P) 2026 XXX" 或 "(C) 2026 XXX")
            copyright_text = info['company']
            # 简单处理：去除符号
            company_clean = ascii_safe(copyright_text)
            if company_clean:
                needs_update['release_company'] = info['company']
                print(f'  Company: {company_clean}')
        else:
            print('  Company: NOT FOUND')

    # 3. 缺流派
    if not current_genre:
        needs_update['genre'] = default_genre
        print(f'  Genre: {default_genre} (default)')

    # 更新数据库
    if needs_update:
        set_clause = ', '.join([f'{k}=?' for k in needs_update.keys()])
        sql = f'UPDATE albums SET {set_clause} WHERE album_id=?'
        values = list(needs_update.values()) + [album_id]
        cur.execute(sql, values)
        print(f'  DB: updated')
    else:
        print(f'  DB: no update needed')

    time.sleep(0.3)

conn.commit()
conn.close()

print('\n=== Export database.sql ===')
conn = sqlite3.connect(DB)
with open(r'C:\Users\qujt\.qclaw\workspace\database.sql', 'w', encoding='utf-8') as f:
    for line in conn.iterdump():
        f.write(line + '\n')
conn.close()
print('Done')
