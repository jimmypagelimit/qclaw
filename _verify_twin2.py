import urllib.request, json
url = 'http://localhost:3456/api/albums?sort=listen&dir=desc&limit=5'
r = json.loads(urllib.request.urlopen(url).read())
for a in r['albums']:
    if 'Twin' in a['album_name'] or 'Fantasy' in a['album_name']:
        print(f"FOUND: {a['album_name']} - {a['artist']}: total={a['total_listen_count']}, year={a.get('year_listen_count','?')}")
        break
else:
    print('Twin Fantasy not in top 5, checking all...')
    for a in r['albums']:
        if 'Twin' in a['album_name']:
            print(f"FOUND: {a['album_name']}")
            break
