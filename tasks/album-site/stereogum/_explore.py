# -*- coding: utf-8 -*-
import urllib.request, re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# 从首页和RSS探索Stereogum结构
urls = {
    '首页': 'https://stereogum.com/',
    'RSS': 'https://www.stereogum.com/feed/',
    '单篇music': 'https://stereogum.com/2502199/la-securites-bingo-is-the-art-punk-party-record-your-weekend-needs/music/',
}

for name, url in urls.items():
    try:
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=10)
        content = resp.read().decode('utf-8', errors='ignore')
        print('=== ' + name + ' (' + str(len(content)) + ' bytes) ===')

        if name == 'RSS':
            items = re.split(r'<item>', content)
            print('RSS Items:', len(items)-1)
            for item in items[1:6]:
                t = re.search(r'<title>(.*?)</title>', item, re.DOTALL)
                l = re.search(r'<link>(https://stereogum\.com/[^<]+)</link>', item)
                cat = re.findall(r'<category><!\[CDATA\[([^\]]+)\]\]></category>', item)
                if t:
                    print('  [' + ', '.join(cat[:2]) + ']', t.group(1).strip()[:50])
        else:
            # 首页/文章页结构
            # 检查是否有结构化数据
            has_review = 'review' in content.lower()[:5000]
            has_schema = 'schema.org' in content or 'application/ld+json' in content
            has_json = '__NEXT_DATA__' in content or '__PRELOADED_STATE__' in content
            print('  has review:', has_review)
            print('  has schema:', has_schema)
            print('  has JSON:', has_json)

            # 提取文章内链接看看结构
            links = re.findall(r'href="(/[^\"]{10,60})"', content)
            cats = set()
            for l in links:
                if any(x in l for x in ['/music/', '/news/', '/reviews/']):
                    cats.add(l)
            print('  分类链接:', list(cats)[:5])
        print()
    except Exception as e:
        print('ERROR: ' + str(e))
        print()
