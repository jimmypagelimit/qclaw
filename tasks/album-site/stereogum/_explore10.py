# -*- coding: utf-8 -*-
import urllib.request, re, json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# Stereogum 年终榜探索
# 从 RSS 或 sitemap 找年榜 URL
test_urls = [
    'https://stereogum.com/lists/stereogums-50-best-albums-of-2024/',
    'https://stereogum.com/lists/stereogums-50-best-albums-2023/',
    'https://stereogum.com/2024/50-best-albums/',
    'https://stereogum.com/the-50-best-albums-of-2024/',
]

for url in test_urls:
    try:
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=8)
        content = resp.read().decode('utf-8', errors='ignore')
        print(url, '->', len(content), 'bytes, status OK')
    except Exception as e:
        print(url, '-> ERROR:', str(e)[-40:])

# 用 sitemap 找所有 lists
print('\n=== Sitemap ===')
sitemap_url = 'https://stereogum.com/post-sitemap.xml'
try:
    req = urllib.request.Request(sitemap_url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=10)
    content = resp.read().decode('utf-8', errors='ignore')
    # 找 lists 相关的 URL
    list_urls = re.findall(r'<loc>(https://stereogum\.com/[^<]+50-best[^<]+)</loc>', content)
    print('50 best lists found:', len(list_urls))
    for u in list_urls[:10]:
        print(' ', u)
    if not list_urls:
        # 扩大范围
        list_urls = re.findall(r'<loc>(https://stereogum\.com/lists/[^<]+)</loc>', content)
        print('All list URLs:', len(list_urls))
        for u in list_urls[:10]:
            print(' ', u)
except Exception as e:
    print('Sitemap error:', e)
