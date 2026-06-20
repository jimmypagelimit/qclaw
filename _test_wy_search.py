import urllib.request, json, urllib.parse, time, sys

sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://music.163.com'
}

def fetch(url):
    req = urllib.request.Request(url, headers=HEADERS)
    resp = urllib.request.urlopen(req, timeout=10)
    return json.loads(resp.read())

# Search with artist name only
tests = [
    ('刺猬乐队', 10),
    ('Hedgehog', 10),
    ('痛仰乐队', 10),
    ('张悬', 10),
    ('Tizzy Bac', 10),
]

for q, t in tests:
    url = f'https://music.163.com/api/search/get?s={urllib.parse.quote(q)}&type={t}&limit=5'
    data = fetch(url)
    albums = data.get('result', {}).get('albums', [])
    print(f'\n"{q}" -> {len(albums)} albums')
    for a in albums[:3]:
        print(f'  id={a["id"]} name={a["name"]} artist={a.get("artist",{}).get("name","?")}')
    time.sleep(0.5)
