"""
批量从网易云下载封面 - 修复版
"""
import sqlite3, json, urllib.request, urllib.parse, os, time, sys

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
COVERS = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers'
HEADERS = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://music.163.com/'}

def log(msg):
    print(msg, flush=True)

def netease_album(album_name, artist_name):
    # Album search
    url = f'https://music.163.com/api/search/get?s={urllib.parse.quote(album_name)}&type=10&limit=15'
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        data = json.loads(urllib.request.urlopen(req, timeout=10).read())
        albums = data.get('result', {}).get('albums', [])
        for a in albums:
            a_artist = a.get('artist', {}).get('name', '')
            # Fuzzy match artist
            if artist_name:
                an = artist_name.lower().replace(' ', '')
                aa = a_artist.lower().replace(' ', '')
                if an in aa or aa in an or any(x in aa for x in an.split() if len(x) > 1):
                    return a.get('picUrl', '')
        # Fallback: first result if good enough
        for a in albums:
            pic = a.get('picUrl', '')
            if pic:
                return pic
    except Exception as e:
        log(f'  Search error: {e}')
    return ''

def netease_song(album_name, artist_name):
    kw = f'{album_name} {artist_name}'.strip()
    url = f'https://music.163.com/api/search/get?s={urllib.parse.quote(kw)}&type=1&limit=10'
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        data = json.loads(urllib.request.urlopen(req, timeout=10).read())
        songs = data.get('result', {}).get('songs', [])
        for s in songs:
            pic = s.get('album', {}).get('picUrl', '')
            if pic:
                return pic
    except Exception as e:
        log(f'  Song search error: {e}')
    return ''

def safe_name(s):
    return ''.join(c for c in str(s) if c not in '<>:"/\\|?*')

def process(album_id, album_name, artist_name):
    log(f'  Searching album...')
    pic = netease_album(album_name, artist_name)
    if not pic:
        log(f'  Trying song search...')
        pic = netease_song(album_name, artist_name)
    
    if not pic:
        return {'id': album_id, 'name': album_name, 'artist': artist_name, 'status': 'NOT_FOUND'}
    
    dest_name = f'{album_id}-{safe_name(artist_name)}-{safe_name(album_name)}.jpg'
    dest = os.path.join(COVERS, dest_name)
    try:
        req = urllib.request.Request(pic, headers=HEADERS)
        data = urllib.request.urlopen(req, timeout=10).read()
        with open(dest, 'wb') as f:
            f.write(data)
        cover_url = f'/covers/{dest_name}'
        conn = sqlite3.connect(DB)
        cur = conn.cursor()
        cur.execute('UPDATE albums SET cover_image_url=? WHERE album_id=?', (cover_url, album_id))
        conn.commit()
        conn.close()
        log(f'  OK: {dest_name} ({len(data)} bytes)')
        return {'id': album_id, 'name': album_name, 'artist': artist_name, 'status': 'OK', 'size': len(data)}
    except Exception as e:
        log(f'  Download error: {e}')
        return {'id': album_id, 'name': album_name, 'artist': artist_name, 'status': 'ERROR', 'error': str(e)}

# Remaining albums after first run (117, 163 already done)
remaining = [
    {'id': 71, 'name': '大只佬', 'artist': 'V是兔子'},
    {'id': 139, 'name': 'The Fly II', 'artist': '苍蝇'},
    {'id': 227, 'name': 'Голос стала (The Voice of Steel)', 'artist': 'Nokturnal Mortum'},
    {'id': 449, 'name': '每一刻都是崭新的', 'artist': '许巍'},
    {'id': 471, 'name': '漩渦重構實驗', 'artist': '猿'},
    {'id': 524, 'name': 'Is It Gonna Happen Again?', 'artist': 'jody积融'},
    {'id': 525, 'name': '脱轨', 'artist': '谢甜柒'},
    {'id': 553, 'name': 'Bitknot', 'artist': 'Feeble Little Horse'},
    {'id': 559, 'name': '荒芜之境', 'artist': '陈楚生'},
]

results = []
for item in remaining:
    log(f'\n[{item["id"]}] {item["name"]} / {item["artist"]}')
    r = process(item['id'], item['name'], item['artist'])
    results.append(r)
    time.sleep(0.5)

with open(r'C:\Users\qujt\.qclaw\workspace\_cover_batch_result.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

ok = [r for r in results if r['status'] == 'OK']
log(f'\n=== Done: {len(ok)}/{len(results)} OK ===')
