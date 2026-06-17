import urllib.request, urllib.parse, json

def search_netease(keyword):
    url = 'https://music.163.com/api/search/get'
    data = urllib.parse.urlencode({'s': keyword, 'type': 10, 'limit': 5, 'offset': 0}).encode()
    req = urllib.request.Request(url, data=data, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://music.163.com'})
    resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
    return resp.get('result', {}).get('albums', [])

results = search_netease('American Road in New Jeresy')
for a in results:
    print(f"ID: {a.get('id')} | Name: {a.get('name')} | Artist: {a.get('artist', {}).get('name')} | PicURL: {a.get('picUrl')}")
