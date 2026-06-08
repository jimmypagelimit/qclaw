import urllib.request, json

try:
    url = 'http://127.0.0.1:3456/api/albums?year=2026&limit=3'
    resp = urllib.request.urlopen(url, timeout=5)
    print(resp.read().decode()[:300])
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8', errors='replace')
    print(f'{e.code}: {body}')
