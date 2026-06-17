import urllib.request, os
url = 'http://p1.music.126.net/FVPq81xtvq1qh5YXplhO_w==/109951173109021880.jpg'
path = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers\523-Angelo De Augustine-Angel in Plainclothes.jpg'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Referer': 'https://music.163.com'})
with open(path, 'wb') as f:
    f.write(urllib.request.urlopen(req, timeout=10).read())
print(f'Downloaded: {os.path.getsize(path)} bytes')
