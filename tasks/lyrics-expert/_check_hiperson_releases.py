import urllib.request, json, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# try other releases
for rel_id, label in [
    ('f1f93c6e-a502-4472-bbb0-0dcc8fb8bfbe', 'Digital Media SG'),
    ('2dac93e2-e9d4-403a-b1c5-24c46db40da7', 'Digital Media XW'),
    ('1161da72-d99d-4c50-9407-57940ddbe261', 'CN CD'),
]:
    url = f'https://musicbrainz.org/ws/2/release/{rel_id}?fmt=json&inc=recordings'
    req = urllib.request.Request(url, headers={'User-Agent': 'AlbumTracker/1.0', 'Accept': 'application/json'})
    r = json.loads(urllib.request.urlopen(req, timeout=15).read())
    
    print(f'=== {label} (title={r.get("title")}) ===')
    for m in r.get('media', []):
        for t in m.get('tracks', []):
            rec = t.get('recording',{})
            print(f'  {t.get("number","?")} {repr(rec.get("title","?"))}')
    print()
