import urllib.request, json, sys

wy_id = sys.argv[1] if len(sys.argv) > 1 else '83491330'
url = f'https://music.163.com/api/album/{wy_id}'
req = urllib.request.Request(url, headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://music.163.com'
})
resp = urllib.request.urlopen(req, timeout=15)
data = json.loads(resp.read())

# 检查结构
print(f"Album: {data.get('album', {}).get('name', 'N/A')}")
print(f"Keys: {list(data.keys())}")

album = data.get('album', {})
print(f"Album keys: {list(album.keys())}")

songs = album.get('songs', [])
print(f"songs type: {type(songs)} len: {len(songs) if isinstance(songs, (list, dict)) else 'N/A'}")

# Try alternate paths
print(f"Has 'songs' at top level: {'songs' in data}")
top_songs = data.get('songs', [])
print(f"top-level songs: {len(top_songs) if isinstance(top_songs, list) else type(top_songs)}")

# Print full response structure (first 2000 chars)
resp_str = json.dumps(data, ensure_ascii=False, indent=2)
print(f"\nFull response preview ({len(resp_str)} chars):")
print(resp_str[:2500])
