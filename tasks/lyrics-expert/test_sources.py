import urllib.request, json, urllib.parse

def test_wy_search(query):
    url = f'https://music.163.com/api/search/get?s={urllib.parse.quote(query)}&type=1&limit=5'
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://music.163.com'
    })
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read())
    songs = data.get('result', {}).get('songs', [])
    return songs

def test_wy_lyric(song_id):
    url = f'https://music.163.com/api/song/lyric?id={song_id}&lv=1&tv=1'
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0', 'Referer': 'https://music.163.com'
    })
    resp = urllib.request.urlopen(req, timeout=10)
    data = json.loads(resp.read())
    lrc = data.get('lrc', {}).get('lyric', '')
    trans = data.get('tlyric', {}).get('lyric', '')
    return lrc[:100] if lrc else '', trans[:100] if trans else ''

# Test 1: 葬尸湖 - 孤雁
print("=== Test 1: 葬尸湖 孤雁 ===")
songs = test_wy_search('葬尸湖 孤雁')
print(f"Found {len(songs)} songs")
for s in songs:
    album_name = s.get('album', {}).get('name', '') if isinstance(s.get('album'), dict) else ''
    print(f"  id={s['id']} {repr(s['name'])} album={repr(album_name)}")

if songs:
    lrc, trans = test_wy_lyric(songs[0]['id'])
    print(f"  LRC length: {len(lrc)}")
    print(f"  Trans length: {len(trans)}")
    if lrc:
        lines = lrc[:200].split('\n')
        print(f"  LRC preview ({len(lines)} lines):")
        for l in lines[:5]:
            print(f"    {l}")

# Test 2: 刺猬 - 赤子白仙
print("\n=== Test 2: 刺猬 赤子白仙 ===")
songs = test_wy_search('刺猬 赤子白仙')
print(f"Found {len(songs)} songs")
for s in songs:
    album_name = s.get('album', {}).get('name', '') if isinstance(s.get('album'), dict) else ''
    print(f"  id={s['id']} {repr(s['name'])} album={repr(album_name)}")

# Test 3: LRCLIB for English
print("\n=== Test 3: LRCLIB Car Seat Headrest ===")
import ssl
ctx = ssl.create_default_context()
url = 'https://lrclib.net/api/search?q=Car+Seat+Headrest+Twin+Fantasy'
resp = urllib.request.urlopen(url, timeout=10)
data = json.loads(resp.read())
print(f"Found {len(data)} results")
if data:
    print(f"  Track: {data[0].get('trackName', 'unknown')}")
    print(f"  Artist: {data[0].get('artistName', 'unknown')}")
    print(f"  Has syncedLyrics: {bool(data[0].get('syncedLyrics'))}")
    print(f"  Has plainLyrics: {bool(data[0].get('plainLyrics'))}")

print("\nAll tests passed!")
