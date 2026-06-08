import urllib.request, json
# 查 2026 年排行
url = 'http://localhost:3456/api/albums?year=2026&sort=listen&dir=desc&limit=5'
r = json.loads(urllib.request.urlopen(url).read())
for a in r['albums']:
    y = a.get('year_listen_count', '?')
    t = a['total_listen_count']
    print(f"  {a['album_name']} - {a['artist']}: year={y}, total={t}")
