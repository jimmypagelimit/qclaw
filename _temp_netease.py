import urllib.request, urllib.parse, json

# 搜索专辑
def search_album(keyword):
    url = 'https://music.163.com/api/search/get'
    data = urllib.parse.urlencode({
        's': keyword,
        'type': 10,  # 专辑
        'limit': 10,
        'offset': 0
    }).encode()
    req = urllib.request.Request(url, data=data, headers={
        'User-Agent': 'Mozilla/5.0',
        'Referer': 'https://music.163.com'
    })
    resp = json.loads(urllib.request.urlopen(req, timeout=10).read())
    return resp.get('result', {}).get('albums', [])

# 搜 The Fencesitters Picture Day
print('=== Picture Day ===')
results = search_album('The Fencesitters Picture Day')
for a in results[:5]:
    print(a.get('name'), '|', a.get('artist', {}).get('name'), '|', a.get('picUrl'))

print()
# 也搜乐队名
print('=== Fencesitters ===')
results = search_album('Fencesitters')
for a in results[:5]:
    print(a.get('name'), '|', a.get('artist', {}).get('name'), '|', a.get('picUrl'))
