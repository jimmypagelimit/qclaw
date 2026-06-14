# -*- coding: utf-8 -*-
import urllib.request, re, json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# 找 The Number Ones 最新文章的准确 URL
url = 'https://stereogum.com/category/columns/the-number-ones/'
req = urllib.request.Request(url, headers=headers)
resp = urllib.request.urlopen(req, timeout=10)
content = resp.read().decode('utf-8', errors='ignore')

# 提取所有链接
links = re.findall(r'href="(https://stereogum\.com/\d{7}/[^"]+)"', content)
print('Total links:', len(links))
for l in links[:20]:
    print(l)
