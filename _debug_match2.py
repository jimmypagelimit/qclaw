import urllib.request, json, urllib.parse, re, sys
sys.stdout.reconfigure(encoding='utf-8')

HEADERS = {"User-Agent": "Mozilla/5.0", "Referer": "https://music.163.com"}
def norm(s):
    return re.sub(r'[\s\-_\.\(\)\[\]\{\}\,\!\?\:\;\'\"\/\\]', '', s).lower()

q = "魏如萱 珍珠刑"
url = f"https://music.163.com/api/search/get?s={urllib.parse.quote(q)}&type=1&limit=50"
req = urllib.request.Request(url, headers=HEADERS)
resp = urllib.request.urlopen(req, timeout=15)
data = json.loads(resp.read())
songs = data.get("result", {}).get("songs", [])

album_norm = norm("珍珠刑")
for s in songs:
    al = s.get("album", {}) or {}
    al_name = al.get("name", "")
    al_norm = norm(al_name)
    match = album_norm == al_norm or album_norm in al_norm or al_norm in album_norm
    if match:
        print(f"  {s['name']} -> norm={norm(s['name'])}")
