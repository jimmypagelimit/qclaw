import urllib.request, re, os

req = urllib.request.Request(
    'https://pitchfork.com/reviews/albums/underscores-u/',
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
)
html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', errors='ignore')

# 找 og:image
m = re.search(r'og:image.*?content="(https://[^"]+)"', html)
if m:
    print('OG IMAGE:', m.group(1))
    url = m.group(1)
else:
    imgs = re.findall(r'(https://media\.pitchfork\.com[^\"]+\.(?:jpg|jpeg|png))', html)
    if imgs:
        print('IMG:', imgs[0])
        url = imgs[0]
    else:
        print('NOT FOUND')
        url = None

if url:
    fname = r'C:\Users\qujt\.qclaw\workspace\album-tracker\public\covers\500-underscores-U.jpg'
    os.makedirs(os.path.dirname(fname), exist_ok=True)
    urllib.request.urlretrieve(url.replace('&amp;', '&'), fname)
    print('Saved:', fname)
