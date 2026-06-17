import urllib.request, os

# 巴蜀文艺复兴 第二章 正确封面
url = 'http://p2.music.126.net/t30p5s1LHDFfqKpsIeyXYg==/109951172815569724.jpg'
path = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers\427-施鑫文月-巴蜀文艺复兴第二章.jpg'

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://music.163.com'})
with open(path, 'wb') as f:
    f.write(urllib.request.urlopen(req, timeout=10).read())

print(f'Downloaded: {os.path.getsize(path)} bytes')
print(f'Path: {path}')
