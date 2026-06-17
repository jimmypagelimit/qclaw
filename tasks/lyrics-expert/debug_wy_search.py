import urllib.request, json, urllib.parse, time

WY_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://music.163.com'
}

def fetch(url):
    req = urllib.request.Request(url, headers=WY_HEADERS)
    resp = urllib.request.urlopen(req, timeout=15)
    return json.loads(resp.read())

def search_tracks_for_album(artist, album):
    """搜索专辑中所有曲目（替代album API）"""
    # 搜索歌曲，用 album 名过滤
    q = f'{artist} {album}'
    url = f'https://music.163.com/api/search/get?s={urllib.parse.quote(q)}&type=1&limit=50'
    data = fetch(url)
    songs = data.get('result', {}).get('songs', [])
    
    tracks = []
    seen_ids = set()
    for s in songs:
        if s['id'] in seen_ids:
            continue
        seen_ids.add(s['id'])
        
        # 检查专辑名是否匹配
        al = s.get('album', {})
        al_name = al.get('name', '') if isinstance(al, dict) else ''
        # 模糊匹配：album名包含搜索内容或搜索内容包含album名
        if (album.lower() in al_name.lower() or al_name.lower() in album.lower()):
            tracks.append({
                'id': s['id'],
                'name': s['name'],
                'position': len(tracks) + 1
            })
    
    return tracks

def search_album_songs_type10(artist, album):
    """用 type=10 搜专辑，然后用 get/album 接口"""
    q = f'{artist} {album}'
    url = f'https://music.163.com/api/search/get?s={urllib.parse.quote(q)}&type=10&limit=5'
    data = fetch(url)
    albums = data.get('result', {}).get('albums', [])
    
    for al in albums:
        al_name = al.get('name', '')
        if album.lower() in al_name.lower() or al_name.lower() in album.lower():
            # 尝试新API路径
            al_id = al['id']
            # 尝试 song/detail API
            song_url = f'https://music.163.com/api/album/{al_id}/detail'
            try:
                req = urllib.request.Request(song_url, headers=WY_HEADERS)
                resp = urllib.request.urlopen(req, timeout=10)
                d = json.loads(resp.read())
                if d.get('code') == 200:
                    songs = d.get('album', {}).get('songs', [])
                    if songs:
                        return [{'id': s['id'], 'name': s['name'], 'position': s.get('no', i+1)} for i, s in enumerate(songs)]
            except:
                pass
    
    return []

# Test
print("=== 魏如萱 藏着不等于遗忘 ===")
tracks = search_tracks_for_album('魏如萱', '藏着不等于遗忘')
print(f"Song search: {len(tracks)} tracks")
for t in tracks[:5]:
    print(f"  {t['position']}: {t['name']} (id={t['id']})")

time.sleep(2)

print("\n=== 刺猬 生之响往 ===")
tracks = search_tracks_for_album('刺猬', '生之响往')
print(f"Song search: {len(tracks)} tracks")
for t in tracks[:5]:
    print(f"  {t['position']}: {t['name']} (id={t['id']})")

time.sleep(2)

print("\n=== 葬尸湖 冬霾 ===")
tracks = search_tracks_for_album('葬尸湖', '冬霾')
print(f"Song search: {len(tracks)} tracks")
for t in tracks[:5]:
    print(f"  {t['position']}: {t['name']} (id={t['id']})")

time.sleep(2)

print("\n=== 尝试 album/detail 路径 ===")
tracks = search_album_songs_type10('魏如萱', '藏着不等于遗忘')
print(f"Album detail: {len(tracks)} tracks")
