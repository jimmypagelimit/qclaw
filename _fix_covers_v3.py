#!/usr/bin/env python3
"""用专辑ID获取正确的网易云封面URL"""
import sqlite3, os, urllib.request, json

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
COVER_DIR = r'C:\Users\qujt\.qclaw\workspace\album-tracker\public\covers'

def download(url, path):
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://music.163.com'
        })
        with urllib.request.urlopen(req, timeout=15) as r:
            data = r.read()
            if len(data) > 5000:
                with open(path, 'wb') as f:
                    f.write(data)
                return len(data)
    except Exception as e:
        print(f'  Error: {e}')
    return 0

conn = sqlite3.connect(DB)
cur = conn.cursor()

print('=== Get covers from album API ===\n')

# 1. 碎梦飞跃 - 外面是夏天 (ID=599)
# 需要先搜索到专辑ID
print('--- ID=599: 碎梦飞跃 - 外面是夏天 ---')

# 搜索专辑
search_url = 'https://music.163.com/api/search/get?s=%E7%A2%8E%E6%A2%A6%E9%A3%9E%E8%B7%83&type=10&limit=10'
try:
    req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://music.163.com'})
    with urllib.request.urlopen(req, timeout=10) as r:
        data = json.loads(r.read())
        albums = data.get('result', {}).get('albums', [])
        print(f'  Found {len(albums)} albums')
        target_album_id = None
        for a in albums:
            name = a.get('name', '')
            artist_info = a.get('artist', {})
            artist = artist_info.get('name', '') if isinstance(artist_info, dict) else str(artist_info)
            print(f'  - {name} by {artist}')
            if '外面是夏天' in name:
                target_album_id = a.get('id')
                pic_id = a.get('picId')
                print(f'    MATCH! albumId={target_album_id}, picId={pic_id}')
                break
        
        if target_album_id:
            # 用专辑API获取封面
            album_api = f'https://music.163.com/api/album/get?id={target_album_id}'
            req2 = urllib.request.Request(album_api, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://music.163.com'})
            with urllib.request.urlopen(req2, timeout=10) as r2:
                album_data = json.loads(r2.read())
                if album_data.get('code') == 200:
                    album_info = album_data.get('album', {})
                    pic_url = album_info.get('picUrl', '')
                    pic_str = album_info.get('picStr', '')
                    print(f'  picUrl: {pic_url}')
                    print(f'  picStr: {pic_str}')
                    
                    # 下载封面
                    cover_file = '599-碎梦飞跃-外面是夏天.jpg'
                    cover_path = os.path.join(COVER_DIR, cover_file)
                    if pic_url:
                        size = download(pic_url, cover_path)
                        if size > 0:
                            cur.execute('UPDATE albums SET cover_image_url=? WHERE album_id=?',
                                        (f'/covers/{cover_file}', 599))
                            print(f'  SUCCESS! ({size} bytes)')
except Exception as e:
    print(f'  Error: {e}')

print()

# 2. 郑源 - 擦肩而过 (ID=596) - album ID from search was 3847xxx range
# Let's try the specific album
print('--- ID=596: 郑源 - 擦肩而过 ---')

# 用已知专辑ID获取
album_api = 'https://music.163.com/api/album/get?id=384720601'  # rough estimate
try:
    req = urllib.request.Request(album_api, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://music.163.com'})
    with urllib.request.urlopen(req, timeout=10) as r:
        album_data = json.loads(r.read())
        print(f'  API code: {album_data.get("code")}')
        if album_data.get('code') == 200:
            album_info = album_data.get('album', {})
            name = album_info.get('name', '')
            print(f'  Album: {name}')
            pic_url = album_info.get('picUrl', '')
            print(f'  picUrl: {pic_url}')
            
            if pic_url and '擦肩' in name:
                cover_file = '596-郑源-擦肩而过.jpg'
                cover_path = os.path.join(COVER_DIR, cover_file)
                size = download(pic_url, cover_path)
                if size > 0:
                    cur.execute('UPDATE albums SET cover_image_url=? WHERE album_id=?',
                                (f'/covers/{cover_file}', 596))
                    print(f'  SUCCESS! ({size} bytes)')
except Exception as e:
    print(f'  Error: {e}')

conn.commit()
conn.close()

print('\n=== Export ===')
conn = sqlite3.connect(DB)
with open(r'C:\Users\qujt\.qclaw\workspace\database.sql', 'w', encoding='utf-8') as f:
    for line in conn.iterdump():
        f.write(line + '\n')
conn.close()
print('Done')
