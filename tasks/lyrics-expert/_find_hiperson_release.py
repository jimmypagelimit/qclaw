import urllib.request, json, sys, time
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# release-group -> releases
rg_id = '7471bdc6-f82a-4476-822d-7f025c045b7b'

url = f'https://musicbrainz.org/ws/2/release?query=rgid:{rg_id}&fmt=json&limit=10'
req = urllib.request.Request(url, headers={'User-Agent': 'AlbumTracker/1.0', 'Accept': 'application/json'})
r = json.loads(urllib.request.urlopen(req, timeout=15).read())

print('Releases:')
for rel in r.get('releases', []):
    rid = rel.get('id','?')
    title = rel.get('title','?')
    date = rel.get('date','?')
    status = rel.get('status','?')
    country = rel.get('country','?')
    fmt = rel.get('media',[{}])[0].get('format','?') if rel.get('media') else '?'
    print(f'  {rid} {title} ({date}) {status} {country} [{fmt}]')
