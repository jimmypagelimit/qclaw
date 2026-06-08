import urllib.request, json

data = json.loads(urllib.request.urlopen('http://127.0.0.1:3456/api/artists?limit=5', timeout=5).read())
for a in data['artists']:
    name = a.get('artist') or a.get('name')
    img = a.get('image_url')
    print(f'{name}: {img}')
