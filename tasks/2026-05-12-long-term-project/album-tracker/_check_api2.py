import urllib.request, json

# 直接看 2026 年列表里有没有 Paul
try:
    url = 'http://127.0.0.1:3456/api/albums?year=2026&offset=0&limit=200'
    data = json.loads(urllib.request.urlopen(url, timeout=5).read())
    print(f'Total 2026 albums: {data.get("total", 0)}')
    
    # 找 Paul
    for a in data.get('albums', []):
        if 'Paul' in (a.get('artist') or '') or 'Dungeon' in (a.get('album_name') or ''):
            print(f"FOUND: {a.get('album_name')} - {a.get('artist')} (ID: {a.get('album_id')})")
            
    # 按 album_id 排序看最大 ID
    ids = [a.get('album_id') for a in data.get('albums', []) if a.get('album_id')]
    print(f'\nAlbum ID range: {min(ids) if ids else "N/A"} - {max(ids) if ids else "N/A"}')
    
    # 看有没有 540
    if 540 in ids:
        print('ID 540 is in list')
    else:
        print('ID 540 NOT in list - checking why...')
        
except Exception as e:
    print(f'Error: {e}')
