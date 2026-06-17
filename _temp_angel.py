import urllib.request, urllib.parse, json

def search_album(keyword):
    url = 'https://music.163.com/api/search/get'
    data = urllib.parse.urlencode({'s': keyword, 'type': 10, 'limit': 5, 'offset': 0}).encode()
    req = urllib.request.Request(url, data=data, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://music.163.com'})
    resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
    return resp.get('result', {}).get('albums', [])

results = search_album('Angel in Plainclothes')
for a in results[:5]:
    print(a.get('name'), '|', a.get('artist', {}).get('name'), '|', a.get('picUrl'))
