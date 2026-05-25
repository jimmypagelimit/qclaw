import urllib.request, json, os

# Download correct cover from Deezer
url = "https://api.deezer.com/search/album?q=car+seat+headrest+twin+fantasy"
resp = urllib.request.urlopen(url, timeout=10)
data = json.loads(resp.read())

cover_dir = r'C:\Users\qujt\.qclaw\workspace\covers'
for album in data['data']:
    if 'Twin Fantasy' in album['title']:
        img_url = album['cover_xl'] or album['cover_big'] or album['cover_medium'] or album['cover']
        print(f"Found: {album['title']} - {img_url}")
        out = os.path.join(cover_dir, '323-Car_Seat_Headrest-Twin_Fantasy.jpg')
        urllib.request.urlretrieve(img_url, out)
        size = os.path.getsize(out)
        print(f"Downloaded: {size} bytes")
        break