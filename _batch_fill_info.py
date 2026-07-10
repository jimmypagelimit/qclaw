#!/usr/bin/env python3
"""批量补全专辑基本信息：封面+发行公司+流派"""
import sqlite3, os, urllib.request, json, time

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
COVER_DIR = r'C:\Users\qujt\.qclaw\workspace\album-tracker\public\covers'

def safe_filename(s):
    """安全文件名"""
    return "".join(c for c in s if c not in r'\\/:*?"<>|').strip()

def download_cover(url, path):
    """下载封面"""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = r.read()
            if len(data) > 5000:
                with open(path, 'wb') as f:
                    f.write(data)
                return len(data)
    except Exception as e:
        print(f'  下载失败: {e}')
    return 0

def itunes_search(artist, album):
    """从iTunes搜索专辑信息"""
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
                            'company': res.get('copyright', '').split(' ')[0] if res.get('copyright') else '',
                            'genre': res.get('primaryGenreName', ''),
                        }
                # 找不到精确匹配，返回第一个
                res = data['results'][0]
                artwork = res.get('artworkUrl100', '').replace('100x100', '600x600')
                return {
                    'cover_url': artwork,
                    'company': res.get('copyright', '').split(' ')[0] if res.get('copyright') else '',
                    'genre': res.get('primaryGenreName', ''),
                }
    except Exception as e:
        print(f'  iTunes搜索失败: {e}')
    return None

# 专辑列表（需要补全的）
albums = [
    {'id': 602, 'artist': 'The Microphones', 'album': 'The Glow, Pt. 2', 'year': 2001, 'genre': 'Indie Rock'},
    {'id': 601, 'artist': 'The Cure', 'album': 'Songs of a Lost World', 'year': 2024, 'genre': 'Post-Punk'},
    {'id': 599, 'artist': '碎梦飞跃', 'album': '外面是夏天', 'year': 2026, 'genre': 'Indie Rock'},
    {'id': 598, 'artist': 'Ryan Beatty', 'album': 'Sweet Fortune', 'year': 2026, 'genre': 'R&B'},
    {'id': 597, 'artist': 'At The Gates', 'album': 'The Ghost of a Future Dead', 'year': 2026, 'genre': 'Melodic Death Metal'},
    {'id': 596, 'artist': '郑源', 'album': '擦肩而过', 'year': 2008, 'genre': 'Mandopop'},
    {'id': 595, 'artist': 'Fires in the Distance', 'album': 'Circadian Promise', 'year': 2026, 'genre': 'Post-Metal'},
    {'id': 594, 'artist': 'Warning', 'album': 'Rituals of Shame', 'year': 2026, 'genre': 'Doom Metal'},
    {'id': 593, 'artist': 'Pixies', 'album': 'Doolittle', 'year': 1989, 'genre': 'Alternative Rock'},
    # ID=600 宋冬野已有公司，只补genre
]

conn = sqlite3.connect(DB)
cur = conn.cursor()

print('=== 批量补全专辑基本信息 ===\n')

results = []

for a in albums:
    album_id = a['id']
    artist = a['artist']
    album_name = a['album']
    year = a['year']
    default_genre = a['genre']

    print(f'--- {artist} - {album_name} (ID={album_id}) ---')

    # 查询当前状态
    cur.execute('SELECT cover_image_url, release_company, genre FROM albums WHERE album_id=?', (album_id,))
    row = cur.fetchone()
    current_cover, current_company, current_genre = row

    needs_update = {}
    new_cover_path = None

    # 1. 如果缺封面，从iTunes下载
    if not current_cover:
        print('  缺封面，从iTunes搜索...')
        info = itunes_search(artist, album_name)
        if info and info['cover_url']:
            cover_filename = f'{album_id}-{safe_filename(artist)}-{safe_filename(album_name)}.jpg'
            cover_path = os.path.join(COVER_DIR, cover_filename)
            size = download_cover(info['cover_url'], cover_path)
            if size > 0:
                needs_update['cover_image_url'] = f'/covers/{cover_filename}'
                print(f'  封面下载成功: {size} bytes')
                new_cover_path = cover_path
            else:
                print('  封面下载失败')
        else:
            print('  iTunes未找到封面')
    else:
        print(f'  封面已有: {current_cover}')

    # 2. 如果缺发行公司，从iTunes获取
    if not current_company:
        if not info:
            info = itunes_search(artist, album_name)
        if info and info['company']:
            needs_update['release_company'] = info['company']
            print(f'  发行公司: {info["company"].encode("ascii", "ignore").decode()}')
        else:
            print('  iTunes未找到发行公司')

    # 3. 如果缺流派，用默认值
    if not current_genre:
        needs_update['genre'] = default_genre
        print(f'  流派: {default_genre}')

    # 更新数据库
    if needs_update:
        set_clause = ', '.join([f'{k}=?' for k in needs_update.keys()])
        sql = f'UPDATE albums SET {set_clause} WHERE album_id=?'
        values = list(needs_update.values()) + [album_id]
        cur.execute(sql, values)
        print(f'  已更新: {list(needs_update.keys())}')
    else:
        print('  无需更新')

    results.append({
        'id': album_id,
        'artist': artist,
        'album': album_name,
        'updates': needs_update,
        'cover_path': new_cover_path
    })
    print()
    time.sleep(0.5)  # 避免请求过快

conn.commit()
conn.close()

print('=== 导出 database.sql ===')
conn = sqlite3.connect(DB)
with open(r'C:\Users\qujt\.qclaw\workspace\database.sql', 'w', encoding='utf-8') as f:
    for line in conn.iterdump():
        f.write(line + '\n')
conn.close()
print('已导出')

print('\n=== 完成 ===')
print(f'处理了 {len(results)} 张专辑')
