"""
批量从网易云下载封面
"""
import sqlite3, json, urllib.request, urllib.parse, os, time

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
COVERS = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers'

HEADERS = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://music.163.com/'}

def netease_search_album(album_name, artist_name):
    # Try album search first
    kw = album_name
    url = f'https://music.163.com/api/search/get?s={urllib.parse.quote(kw)}&type=10&limit=10'
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        data = json.loads(urllib.request.urlopen(req, timeout=10).read())
        albums = data.get('result', {}).get('albums', [])
        for a in albums:
            a_artist = a.get('artist', {}).get('name', '')
            if artist_name and (artist_name in a_artist or a_artist in artist_name):
                return a.get('picUrl', '')
        # Fall back to song search
        kw2 = f'{album_name} {artist_name}'
        url2 = f'https://music.163.com/api/search/get?s={urllib.parse.quote(kw2)}&type=1&limit=5'
        req2 = urllib.request.Request(url2, headers=HEADERS)
        data2 = json.loads(urllib.request.urlopen(req2, timeout=10).read())
        songs = data2.get('result', {}).get('songs', [])
        for s in songs:
            pic = s.get('album', {}).get('picUrl', '')
            if pic:
                return pic
    except Exception as e:
        print(f'  Search error: {e}')
    return ''

def safe_filename(s):
    return ''.join(c for c in s if c not in '<>:"/\\|?*')

results = []
with open(r'C:\Users\qujt\.qclaw\workspace\_missing_covers.json', 'r', encoding='utf-8') as f:
    albums = json.load(f)

for item in albums:
    album_id = item['id']
    album_name = item['name']
    artist_name = item['artist']
    print(f'\n[{album_id}] {album_name} / {artist_name}')
    
    pic_url = netease_search_album(album_name, artist_name)
    
    if pic_url:
        dest_name = f'{album_id}-{safe_filename(artist_name)}-{safe_filename(album_name)}.jpg'
        dest = os.path.join(COVERS, dest_name)
        try:
            req = urllib.request.Request(pic_url, headers=HEADERS)
            data = urllib.request.urlopen(req, timeout=10).read()
            with open(dest, 'wb') as f:
                f.write(data)
            cover_url = f'/covers/{dest_name}'
            
            conn = sqlite3.connect(DB)
            cur = conn.cursor()
            cur.execute('UPDATE albums SET cover_image_url=? WHERE album_id=?', (cover_url, album_id))
            conn.commit()
            conn.close()
            
            print(f'  OK: {dest_name} ({len(data)} bytes)')
            results.append({'id': album_id, 'name': album_name, 'artist': artist_name, 'status': 'OK', 'size': len(data)})
        except Exception as e:
            print(f'  Download error: {e}')
            results.append({'id': album_id, 'name': album_name, 'artist': artist_name, 'status': 'ERROR', 'error': str(e)})
    else:
        print(f'  NOT FOUND on NetEase')
        results.append({'id': album_id, 'name': album_name, 'artist': artist_name, 'status': 'NOT_FOUND'})
    
    time.sleep(0.5)

with open(r'C:\Users\qujt\.qclaw\workspace\_cover_batch_result.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

ok = [r for r in results if r['status'] == 'OK']
print(f'\n=== Done: {len(ok)}/{len(results)} OK ===')
