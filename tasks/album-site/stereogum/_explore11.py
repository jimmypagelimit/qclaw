# -*- coding: utf-8 -*-
import urllib.request, re, json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# 从首页找 50 best 链接
url = 'https://stereogum.com/'
req = urllib.request.Request(url, headers=headers)
resp = urllib.request.urlopen(req, timeout=10)
content = resp.read().decode('utf-8', errors='ignore')

# 找所有包含 50 best 或 album 或 year-end 的链接
all_links = re.findall(r'href="(https://stereogum\.com/[^"]+)"', content)
print('Total links:', len(all_links))

# 关键词过滤
keywords = ['50-best', 'best-albums', 'year-end', '-albums-', 'albums-of-']
for kw in keywords:
    matches = [l for l in all_links if kw in l.lower()]
    if matches:
        print('\n[' + kw + ']')
        for m in matches[:5]:
            print(' ', m)

# 从 __NEXT_DATA__ 的 homepageProps 找特色内容
match = re.search(r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.+?)</script>', content, re.DOTALL)
if match:
    data = json.loads(match.group(1))
    hp = data['props']['pageProps']
    print('\npageProps keys:', list(hp.keys()))

    # 找 featured posts
    for k in ['featuredPosts', 'latestPosts', 'posts', 'editorsPicks', 'curated']:
        if k in hp:
            posts = hp[k]
            if isinstance(posts, list):
                print('\n' + k + ':', len(posts), 'posts')
                for p in posts[:3]:
                    if isinstance(p, dict):
                        print(' -', p.get('title', p.get('slug', ''))[:50])
                    else:
                        print(' -', str(p)[:50])
