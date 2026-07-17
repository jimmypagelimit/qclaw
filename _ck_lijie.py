import urllib.request, json

r = urllib.request.urlopen('http://localhost:3456/api/albums?page=1&limit=1000', timeout=15)
data = json.loads(r.read())
for alb in data.get('albums', []):
    if alb.get('artist') == '李杰' and '解梦' in (alb.get('album_name') or ''):
        print(f'Found: [{alb.get("album_id")}] {alb.get("artist")} - {alb.get("album_name")}')
        break
    if alb.get('artist') == '李杰':
        print(f'  [{alb.get("album_id")}] {alb.get("album_name")}')
else:
    print('李杰 not found in DB')
