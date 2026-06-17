import urllib.request, re

url = 'https://carseatheadrest.bandcamp.com/album/teens-of-style'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
html = urllib.request.urlopen(req, timeout=10).read().decode()

# Find og:image
m = re.search(r'og:image.*?content="([^"]+)"', html)
if m:
    print(f'OG Image: {m.group(1)}')
else:
    # Try image pattern
    imgs = re.findall(r'https://[^"]+\.jpg', html)
    for i in imgs[:10]:
        print(i)
