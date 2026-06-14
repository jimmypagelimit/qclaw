import urllib.request, urllib.parse, json

url = 'http://music.163.com/api/search/get/web'
data = urllib.parse.urlencode({'s': 'Tizzy Bac 夏季热', 'type': 10, 'limit': 5})
req = urllib.request.Request(url, data=data.encode(), headers={'User-Agent': 'Mozilla/5.0'})
resp = json.loads(urllib.request.urlopen(req).read())

# Extract album info and cover
items = resp.get('result', {}).get('albums', [])
for a in items:
    print(f"Name: {a.get('name')}")
    print(f"Artist: {a.get('artist', {}).get('name')}")
    print(f"Year: {a.get('publishTime', 0) // 1000}")
    print(f"ID: {a.get('id')}")
    # Cover
    pic = a.get('pic')
    print(f"Pic: {pic}")
    print()
