import urllib.request, json

r = urllib.request.urlopen('http://localhost:3456/api/albums?page=1&limit=1000', timeout=15)
data = json.loads(r.read())
found = None
for alb in data.get('albums', []):
    if alb.get('artist') == '苏醒' and '秋天' in (alb.get('album_name') or ''):
        found = alb
        break

if found:
    album_id = found.get('album_id')
    print(f'Found: {found.get("artist")} - {found.get("album_name")} (id={album_id})')
    req = urllib.request.Request(
        f'http://localhost:3456/api/albums/{album_id}/listen',
        data=json.dumps({'count': 1}).encode(),
        headers={'Content-Type': 'application/json'}
    )
    rr = urllib.request.urlopen(req, timeout=10)
    print('Result:', json.loads(rr.read()).get('success'))
else:
    print('Not found, searching partial match...')
    for alb in data.get('albums', []):
        if alb.get('artist') == '苏醒':
            print(f'  [{alb.get("album_id")}] {alb.get("album_name")}')
