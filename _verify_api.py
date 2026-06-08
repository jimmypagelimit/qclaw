import urllib.request, json
r = json.loads(urllib.request.urlopen('http://localhost:3456/api/albums?year=2026&limit=5&sort=listen&dir=desc').read())
for a in r['albums']:
    print(f"{a['album_name']} - {a['artist']}: year={a.get('year_listen_count','')}, total={a['total_listen_count']}")
