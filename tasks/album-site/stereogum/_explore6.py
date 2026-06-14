# -*- coding: utf-8 -*-
import urllib.request, re, json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

url = 'https://stereogum.com/category/columns/the-number-ones/'
req = urllib.request.Request(url, headers=headers)
resp = urllib.request.urlopen(req, timeout=10)
content = resp.read().decode('utf-8', errors='ignore')

# 用更宽松的正则找链接
links = re.findall(r'https://stereogum\.com/[a-z0-9-]+/[a-z0-9-]+/', content)
unique = list(dict.fromkeys(links))  # preserve order, remove dupes
print('Unique links:', len(unique))
for l in unique[:15]:
    print(l)
