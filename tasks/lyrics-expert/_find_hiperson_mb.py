import urllib.request, json, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

def mb_search(query, limit=15):
    url = f'https://musicbrainz.org/ws/2/release-group?query={urllib.parse.quote(query)}&fmt=json&limit={limit}'
    req = urllib.request.Request(url, headers={'User-Agent': 'AlbumTracker/1.0', 'Accept': 'application/json'})
    return json.loads(urllib.request.urlopen(req, timeout=15).read())

import urllib.parse

# Search Hiperson / 海朋森
queries = [
    'artist:Hiperson',
    'artist:海朋森',
]
for q in queries:
    print(f'=== {q} ===')
    r = mb_search(q)
    for rg in r.get('release-groups', []):
        artists = ','.join(ac.get('name','?') for ac in rg.get('artist-credit',[]))
        title = rg.get('title','?')
        rid = rg.get('id','?')
        rtype = rg.get('primary-type','?')
        print(f'  RG: {title} ({rid}) type={rtype} artist={artists}')
    print()
    time.sleep(1)
