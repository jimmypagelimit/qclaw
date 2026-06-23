import sys
sys.stdout.reconfigure(encoding='utf-8')
print('start', flush=True)
import urllib.request, json, time
print('imports done', flush=True)
url = 'https://lrclib.net/api/search?q=Nirvana%20Smells%20Like%20Teen%20Spirit'
req = urllib.request.Request(url, headers={'User-Agent': 'Test/1.0'})
r = urllib.request.urlopen(req, timeout=8)
d = json.loads(r.read())
print('results:', len(d), flush=True)
print('DONE', flush=True)
