import urllib.request, json, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

mbid = '12c34412-9525-4224-b09c-47e6a2ddfb30'

# check what this MBID is
url = f'https://musicbrainz.org/ws/2/release/{mbid}?fmt=json&inc=artist-credits+recordings'
try:
    req = urllib.request.Request(url, headers={'User-Agent': 'AlbumTracker/1.0', 'Accept': 'application/json'})
    r = json.loads(urllib.request.urlopen(req, timeout=15).read())
    print('Title:', r.get('title'))
    print('Artist:', r.get('artist-credit',[{}])[0].get('name','?'))
    print('Date:', r.get('date'))
    print()
    if 'media' in r:
        for m in r['media']:
            print(f'  Disc {m.get("position","?")}: {m.get("track-count","?")} tracks')
            for t in m.get('tracks',[]):
                print(f'    {t.get("number","?")} {t.get("title","?")}')
except Exception as e:
    print(f'Error: {type(e).__name__}: {e}')
