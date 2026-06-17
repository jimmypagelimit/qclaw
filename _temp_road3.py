import urllib.request, os

url = 'http://p2.music.126.net/u_0jTbu6soFd5S7CWySN-Q==/109951172841188341.jpg'
path = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers\484-American Road In New Jersey-American Road in New Jersey.jpg'

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://music.163.com'})
with open(path, 'wb') as f:
    f.write(urllib.request.urlopen(req, timeout=10).read())

print(f'Downloaded: {os.path.getsize(path)} bytes')
