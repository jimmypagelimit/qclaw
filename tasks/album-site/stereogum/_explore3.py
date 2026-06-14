# -*- coding: utf-8 -*-
import urllib.request, re, json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# 检查 Album of the Week 和 album-reviews 分类页
urls = [
    ('album-of-the-week', 'https://stereogum.com/category/reviews/album-of-the-week/'),
    ('album-reviews', 'https://stereogum.com/category/reviews/album-review/'),
]

for name, url in urls:
    try:
        req = urllib.request.Request(url, headers=headers)
        resp = urllib.request.urlopen(req, timeout=10)
        content = resp.read().decode('utf-8', errors='ignore')
        print('=== ' + name + ' (' + str(len(content)) + ' bytes) ===')

        # 提取文章标题
        titles = re.findall(r'<h2[^>]*>([^<]+)</h2>', content)
        for t in titles[:8]:
            print(' h2:', t.strip()[:60])

        links = re.findall(r'href="(https://stereogum\.com/[^"]+)"[^>]*>\s*([^<\n]{10,80})\s*</a>', content)
        for link, title in links[:8]:
            print(' link:', title.strip()[:55], '|', link[:70])

        # 检查是否有评分结构
        has_rating = 'rating' in content.lower() or 'score' in content.lower() or 'out of' in content.lower()
        has_schema = 'schema.org' in content
        print(' has_rating:', has_rating, '| has_schema:', has_schema)
        print()
    except Exception as e:
        print('ERROR: ' + str(e))
        print()

# 深入分析一篇 Album of the Week 看看有没有评分
print('=== 分析 Album of the Week 详情 ===')
aow_url = 'https://stereogum.com/category/reviews/album-of-the-week/'
req = urllib.request.Request(aow_url, headers=headers)
resp = urllib.request.urlopen(req, timeout=10)
content = resp.read().decode('utf-8', errors='ignore')

# 找最新文章的链接
article_links = re.findall(r'href="(https://stereogum\.com/\d+[^"]+/)"', content)
if article_links:
    article_url = article_links[0]
    print('First article:', article_url)
    req2 = urllib.request.Request(article_url, headers=headers)
    resp2 = urllib.request.urlopen(req2, timeout=10)
    article_content = resp2.read().decode('utf-8', errors='ignore')

    # schema.org 数据
    schemas = re.findall(r'application/ld\+json[^>]*>([^<]+)<', article_content)
    for s in schemas[:2]:
        try:
            d = json.loads(s)
            print('Schema type:', d.get('@type'))
            print('Schema headline:', d.get('headline', '')[:60])
            print('Schema keys:', list(d.keys()))
        except:
            pass

    # 检查页面内容
    has_rating = any(x in article_content.lower() for x in ['rating', 'score', 'out of', 'stars', 'grade'])
    print('Has rating data:', has_rating)
    # 找 BNM 标记
    bnms = re.findall(r'(BNM|Best New Music|Best New Album)', article_content)
    print('BNM tags:', bnms[:3])
