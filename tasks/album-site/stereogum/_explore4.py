# -*- coding: utf-8 -*-
import urllib.request, re, json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# Stereogum 的核心栏目分析
columns = {
    'The Number Ones': 'https://stereogum.com/category/columns/the-number-ones/',
    'Month In Metal': 'https://stereogum.com/category/columns/breaking-the-oath/',
    'Month In Pop': 'https://stereogum.com/category/columns/chained-to-the-rhythm/',
    'Month In Hardcore': 'https://stereogum.com/category/columns/let-the-roundup-begin/',
}

for name, url in columns.items():
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=10)
    content = resp.read().decode('utf-8', errors='ignore')
    print('=== ' + name + ' (' + str(len(content)) + ' bytes) ===')

    # 提取最新文章
    articles = re.findall(r'href="(https://stereogum\.com/\d+[^"]+/)"\s*[^>]*>\s*([^<\n]{5,80})\s*</a>', content)
    seen = set()
    for link, title in articles[:5]:
        t = title.strip()
        if t and t not in seen and len(t) > 10:
            seen.add(t)
            print(' ', t[:60])

    # 检查是否有排名/评分
    has_rank = any(x in content.lower() for x in ['rank', 'chart', 'number ones', '#1', '#2', '#3'])
    has_schema = 'schema.org' in content
    print(' has_rank:', has_rank, '| has_schema:', has_schema)
    print()

# 深入分析 The Number Ones 单篇（每周排名）
print('=== The Number Ones 单篇分析 ===')
tno_url = 'https://stereogum.com/category/columns/the-number-ones/'
req = urllib.request.Request(tno_url, headers=headers)
resp = urllib.request.urlopen(req, timeout=10)
content = resp.read().decode('utf-8', errors='ignore')

# 找最新文章的链接
first_link = re.search(r'href="(https://stereogum\.com/\d{7}/[^/]+/)"', content)
if first_link:
    article_url = first_link.group(1)
    print('Latest article:', article_url)
    req2 = urllib.request.Request(article_url, headers=headers)
    resp2 = urllib.request.urlopen(req2, timeout=10)
    ac = resp2.read().decode('utf-8', errors='ignore')

    # 提取 schema.org 数据
    schemas = re.findall(r'application/ld\+json[^>]*>([^<]+)<', ac)
    for s in schemas[:3]:
        try:
            d = json.loads(s)
            print('Schema type:', d.get('@type'))
            print('Headline:', d.get('headline', '')[:60])
            if 'itemListElement' in d:
                print('List elements:', len(d['itemListElement']))
                for item in d['itemListElement'][:3]:
                    print('  -', item.get('name', item.get('position', '')), str(item.get('position', '')))
        except Exception as e:
            print('err:', e, s[:100])

    # 找歌曲排名
    songs = re.findall(r'(#\d+)\s*[-–]\s*([^<"\n]{5,60})', ac)
    if songs:
        print('\nSongs found:', len(songs))
        for rank, name in songs[:5]:
            print(' ', rank, '-', name.strip()[:50])
