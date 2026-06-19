import urllib.request, json, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

rel_id = '1161da72-d99d-4c50-9407-57940ddbe261'  # 成长小说 CN CD

url = f'https://musicbrainz.org/ws/2/release/{rel_id}?fmt=json&inc=recordings+artist-credits'
req = urllib.request.Request(url, headers={'User-Agent': 'AlbumTracker/1.0', 'Accept': 'application/json'})
r = json.loads(urllib.request.urlopen(req, timeout=15).read())

print('Title:', r.get('title'))
print('Artist:', r.get('artist-credit',[{}])[0].get('name','?'))
print('Date:', r.get('date'))
print()

for m in r.get('media', []):
    print(f'Disc {m.get("position","?")} ({m.get("format","?")}) {m.get("track-count","?")} tracks')
    for t in m.get('tracks', []):
        dur = t.get('recording',{}).get('length')
        dur_str = str(int(dur/1000)) + 's' if dur else '-'
        print(f'  {t.get("number","?")} {t.get("recording",{}).get("title","?")} ({dur_str})')
