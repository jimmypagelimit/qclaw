import urllib.request, json

# Test basic stats
try:
    data = json.loads(urllib.request.urlopen('http://127.0.0.1:3456/api/stats', timeout=5).read())
    print('Stats OK:', json.dumps(data, indent=2)[:200])
except Exception as e:
    print(f'Stats error: {e}')

# Test albums without year
try:
    data = json.loads(urllib.request.urlopen('http://127.0.0.1:3456/api/albums?offset=0&limit=3', timeout=5).read())
    print(f'Albums (no year): total={data.get("total")}')
except Exception as e:
    print(f'Albums error: {e}')

# Test year with error details
try:
    url = 'http://127.0.0.1:3456/api/albums?year=2026&offset=0&limit=5'
    resp = urllib.request.urlopen(url, timeout=5)
    data = json.loads(resp.read())
    print(f'Year 2026 OK: total={data.get("total")}')
except urllib.error.HTTPError as e:
    body = e.read().decode('utf-8', errors='replace')
    print(f'Year 2026 error {e.code}: {body}')
