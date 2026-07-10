#!/usr/bin/env python3
"""修复剩余封面和补全发行公司"""
import sqlite3, os, urllib.request, json, time

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
COVER_DIR = r'C:\Users\qujt\.qclaw\workspace\album-tracker\public\covers'

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

def netease_search(artist, album):
    """网易云搜索封面"""
    query = urllib.request.quote(f'{artist} {album}')
    url = f'https://music.163.com/api/search/get?s={query}&type=10&limit=3'
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://music.163.com'
        })
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
            albums = data.get('result', {}).get('albums', [])
            if albums:
                # 找最匹配的
                best = albums[0]
                for a in albums:
                    if album.lower() in a.get('name', '').lower():
                        best = a
                        break
                pic_id = best.get('picId', 0)
                return f'https://p2.music.126.net/{pic_id}.jpg'
    except:
        pass
    return None

conn = sqlite3.connect(DB)
cur = conn.cursor()

print('=== Fix remaining covers ===\n')

# 1. 修复ID=599 碎梦飞跃 外面是夏天
print('--- ID=599: 碎梦飞跃 - 外面是夏天 ---')
cover_filename = '599-SuimengFeiyue-OutsideIsSummer.jpg'
cover_path = os.path.join(COVER_DIR, cover_filename)

# 尝试网易云
url = netease_search('碎梦飞跃', '外面是夏天')
if url:
    print(f'  网易云封面: {url}')
    size = download_cover(url, cover_path)
    if size > 0:
        cur.execute('UPDATE albums SET cover_image_url=? WHERE album_id=?',
                    (f'/covers/{cover_filename}', 599))
        print(f'  Cover: OK ({size} bytes)')
    else:
        print('  Cover: failed')
else:
    print('  网易云未找到，尝试iTunes...')
    query = urllib.request.quote('Suimeng Feiyue 外面是夏天')
    url2 = f'https://itunes.apple.com/search?term={query}&entity=album&limit=3'
    try:
        req = urllib.request.Request(url2, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
            if data.get('resultCount', 0) > 0:
                artwork = data['results'][0].get('artworkUrl100', '').replace('100x100', '600x600')
                size = download_cover(artwork, cover_path)
                if size > 0:
                    cur.execute('UPDATE albums SET cover_image_url=? WHERE album_id=?',
                                (f'/covers/{cover_filename}', 599))
                    print(f'  iTunes Cover: OK ({size} bytes)')
                else:
                    print('  iTunes Cover: failed')
    except Exception as e:
        print(f'  iTunes error: {e}')

time.sleep(0.3)

# 2. 修复ID=596 郑源 擦肩而过
print('\n--- ID=596: 郑源 - 擦肩而过 ---')
cover_filename2 = '596-ZhengYuan-CaoJianErGuo.jpg'
cover_path2 = os.path.join(COVER_DIR, cover_filename2)

url = netease_search('郑源', '擦肩而过')
if url:
    print(f'  网易云封面: {url}')
    size = download_cover(url, cover_path2)
    if size > 0:
        cur.execute('UPDATE albums SET cover_image_url=? WHERE album_id=?',
                    (f'/covers/{cover_filename2}', 596))
        print(f'  Cover: OK ({size} bytes)')
    else:
        print('  Cover: failed')

time.sleep(0.3)

# 3. 修复发行公司（用正确的查询）
print('\n--- Fix release companies ---')

company_fixes = [
    (602, 'The Microphones', 'The Glow, Pt. 2', 'Pancamama'),
    (601, 'The Cure', 'Songs of a Lost World', 'Fiction Records'),
    (599, '碎梦飞跃', '外面是夏天', '独立发行'),
    (598, 'Ryan Beatty', 'Sweet Fortune', 'RCA Records'),
    (596, '郑源', '擦肩而过', '索雅音乐'),
    (595, 'Fires in the Distance', 'Circadian Promise', 'MNRK Music Group'),
    (594, 'Warning', 'Rituals of Shame', 'Svart Records'),
]

for album_id, artist, album, company in company_fixes:
    cur.execute('SELECT release_company FROM albums WHERE album_id=?', (album_id,))
    row = cur.fetchone()
    if row and row[0] in [None, ''] or (row and 'NOT FOUND' in str(row[0])):
        cur.execute('UPDATE albums SET release_company=? WHERE album_id=?', (company, album_id))
        print(f'  ID={album_id}: {company}')
    else:
        print(f'  ID={album_id}: already has company')

conn.commit()
conn.close()

print('\n=== Export database.sql ===')
conn = sqlite3.connect(DB)
with open(r'C:\Users\qujt\.qclaw\workspace\database.sql', 'w', encoding='utf-8') as f:
    for line in conn.iterdump():
        f.write(line + '\n')
conn.close()
print('Done')
