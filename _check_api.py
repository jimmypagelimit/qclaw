import urllib.request, json
r = json.loads(urllib.request.urlopen('http://localhost:3456/api/albums?year=2026&limit=10&sort=listen&dir=desc').read())
for a in r['albums']:
    print(f"id={a['album_id']}, name={a['album_name']}, artist={a['artist']}, year_count={a.get('year_listen_count','')}, total={a['total_listen_count']}, cover={a.get('cover_image_url','')[:30]}")
