import urllib.request, json

# 测试专辑库搜索 API
try:
    url = 'http://127.0.0.1:3456/api/albums?query=Paul&year=2026&offset=0&limit=20'
    data = json.loads(urllib.request.urlopen(url, timeout=5).read())
    print(f'Found {data.get("total", 0)} albums')
    for a in data.get('albums', [])[:5]:
        print(f'  {a.get("album_name")} - {a.get("artist")}')
except Exception as e:
    print(f'Error: {e}')

# 直接搜 Dungeon
try:
    url = 'http://127.0.0.1:3456/api/albums?query=Dungeon&offset=0&limit=10'
    data = json.loads(urllib.request.urlopen(url, timeout=5).read())
    print(f'\nDungeon search: {data.get("total", 0)} albums')
    for a in data.get('albums', []):
        print(f'  {a.get("album_name")} - {a.get("artist")}')
except Exception as e:
    print(f'Error: {e}')
