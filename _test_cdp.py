import urllib.request, json

try:
    resp = urllib.request.urlopen('http://127.0.0.1:9222/json', timeout=5)
    data = json.loads(resp.read())
    print(f'Chrome CDP OK - {len(data)} tabs')
    for t in data:
        url = t.get('url', '?')[:80]
        print(f'  {t["id"]} | {url}')
except Exception as e:
    print(f'ERROR: {e}')
