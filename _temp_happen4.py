import urllib.request, os

url = 'http://p1.music.126.net/BQciQ_KTIys7nW-0cvD2pA==/109951172804703603.jpg'
# 用原始字符串，单引号不转义
path = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers\493-Mitski-Nothing\'s About to Happen to Me.jpg'

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://music.163.com'})
with open(path, 'wb') as f:
    f.write(urllib.request.urlopen(req, timeout=10).read())

print(f'Downloaded: {os.path.getsize(path)} bytes')
