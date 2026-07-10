#!/usr/bin/env python3
"""修复两张困难的封面：碎梦飞跃、郑源"""
import sqlite3, os, urllib.request, json

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
COVER_DIR = r'C:\Users\qujt\.qclaw\workspace\album-tracker\public\covers'

def safe_filename(s):
    return "".join(c for c in s if c not in r'\/:*?"<>|').strip()

def download(url, path):
    print(f'  Downloading: {url[:60]}...')
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
            'Referer': 'https://music.163.com'
        })
        with urllib.request.urlopen(req, timeout=15) as r:
            data = r.read()
            print(f'  Response size: {len(data)} bytes')
            if len(data) > 5000:
                with open(path, 'wb') as f:
                    f.write(data)
                return len(data)
            else:
                print(f'  File too small, might be error page')
                return 0
    except Exception as e:
        print(f'  Error: {e}')
        return 0

conn = sqlite3.connect(DB)
cur = conn.cursor()

print('=== Fix covers ===\n')

# 1. 碎梦飞跃 - 外面是夏天 (ID=599)
print('--- ID=599: 碎梦飞跃 - 外面是夏天 ---')
cover_file = '599-碎梦飞跃-外面是夏天.jpg'
cover_path = os.path.join(COVER_DIR, cover_file)

# 尝试通过API获取正确URL
url = 'https://music.163.com/api/search/get?s=%E7%A2%8E%E6%A2%A6%E9%A3%9E%E8%B6%8A%20%E9%97%B4%E9%9D%A2%E6%98%AF%E5%A4%8F%E5%A4%A9&type=10&limit=5'
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://music.163.com'})
    with urllib.request.urlopen(req, timeout=10) as r:
        data = json.loads(r.read())
        albums = data.get('result', {}).get('albums', [])
        print(f'  API returned {len(albums)} albums')
        if albums:
            for a in albums:
                name = a.get('name', '')
                artist = a.get('artist', {}).get('name', '') if isinstance(a.get('artist'), dict) else str(a.get('artist', ''))
                pic_id = a.get('picId', 0)
                print(f'  Found: {name} by {artist} (picId={pic_id})')
                # 构建封面URL
                if pic_id:
                    # 网易云封面CDN格式
                    cover_url = f'https://p2.music.126.net/{pic_id}.jpg'
                    size = download(cover_url, cover_path)
                    if size > 0:
                        cur.execute('UPDATE albums SET cover_image_url=? WHERE album_id=?',
                                    (f'/covers/{cover_file}', 599))
                        print(f'  SUCCESS! ({size} bytes)')
                        break
                    else:
                        # 尝试另一格式
                        cover_url2 = f'http://p2.music.126.net/{pic_id}.jpg'
                        size2 = download(cover_url2, cover_path)
                        if size2 > 0:
                            cur.execute('UPDATE albums SET cover_image_url=? WHERE album_id=?',
                                        (f'/covers/{cover_file}', 599))
                            print(f'  SUCCESS with http! ({size2} bytes)')
                            break
except Exception as e:
    print(f'  API error: {e}')

print()

# 2. 郑源 - 擦肩而过 (ID=596)
print('--- ID=596: 郑源 - 擦肩而过 ---')
cover_file2 = '596-郑源-擦肩而过.jpg'
cover_path2 = os.path.join(COVER_DIR, cover_file2)

url2 = 'https://music.163.com/api/search/get?s=%E9%84%AD%E6%BA%90%20%E6%93%A6%E8%82%A9%E8%80%8C%E8%BF%87&type=10&limit=5'
try:
    req = urllib.request.Request(url2, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://music.163.com'})
    with urllib.request.urlopen(req, timeout=10) as r:
        data = json.loads(r.read())
        albums = data.get('result', {}).get('albums', [])
        print(f'  API returned {len(albums)} albums')
        if albums:
            for a in albums:
                name = a.get('name', '')
                artist = a.get('artist', {}).get('name', '') if isinstance(a.get('artist'), dict) else str(a.get('artist', ''))
                pic_id = a.get('picId', 0)
                print(f'  Found: {name} by {artist} (picId={pic_id})')
                if pic_id and ('擦肩' in name or '郑源' in artist):
                    cover_url = f'https://p2.music.126.net/{pic_id}.jpg'
                    size = download(cover_url, cover_path2)
                    if size > 0:
                        cur.execute('UPDATE albums SET cover_image_url=? WHERE album_id=?',
                                    (f'/covers/{cover_file2}', 596))
                        print(f'  SUCCESS! ({size} bytes)')
                        break
                    else:
                        cover_url2 = f'http://p2.music.126.net/{pic_id}.jpg'
                        size2 = download(cover_url2, cover_path2)
                        if size2 > 0:
                            cur.execute('UPDATE albums SET cover_image_url=? WHERE album_id=?',
                                        (f'/covers/{cover_file2}', 596))
                            print(f'  SUCCESS with http! ({size2} bytes)')
                            break
except Exception as e:
    print(f'  API error: {e}')

conn.commit()
conn.close()

print('\n=== Export ===')
conn = sqlite3.connect(DB)
with open(r'C:\Users\qujt\.qclaw\workspace\database.sql', 'w', encoding='utf-8') as f:
    for line in conn.iterdump():
        f.write(line + '\n')
conn.close()
print('Done')
