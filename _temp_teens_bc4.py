import urllib.request, os

url = 'https://f4.bcbits.com/img/a2269688042_5.jpg'
path = "C:\\Users\\qujt\\.qclaw\\workspace\\tasks\\2026-05-12-long-term-project\\album-tracker\\public\\covers\\554-Car Seat Headrest-Teens of Style.jpg"

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with open(path, 'wb') as f:
    f.write(urllib.request.urlopen(req, timeout=10).read())

print(f'Downloaded: {os.path.getsize(path)} bytes')

from PIL import Image
img = Image.open(path)
print(f'Size: {img.size}')
