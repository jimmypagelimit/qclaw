import urllib.request, os

# 去掉param参数获取原图
url = 'http://p1.music.126.net/9OmHNQPmyzSN4GQ_8_3m1A==/109951169834376967.jpg'
path = "C:\\Users\\qujt\\.qclaw\\workspace\\tasks\\2026-05-12-long-term-project\\album-tracker\\public\\covers\\426-施鑫文月-巴蜀文艺复兴第一章.jpg"

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://music.163.com'})
with open(path, 'wb') as f:
    f.write(urllib.request.urlopen(req, timeout=10).read())

print(f'Downloaded: {os.path.getsize(path)} bytes')

# 检查图片尺寸
from PIL import Image
img = Image.open(path)
print(f'Size: {img.size}')
