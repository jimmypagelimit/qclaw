# -*- coding: utf-8 -*-
import urllib.request, re, json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# 分析 The Number Ones 单篇文章结构
url = 'https://stereogum.com/2500947/the-number-ones-the-kid-laroi-justin-biebers-stay/'
req = urllib.request.Request(url, headers=headers)
resp = urllib.request.urlopen(req, timeout=10)
content = resp.read().decode('utf-8', errors='ignore')

print('Page length:', len(content))

# 找 schema.org
schemas = re.findall(r'<script[^>]*type="application/ld\+json"[^>]*>([^<]+)</script>', content)
for s in schemas:
    try:
        d = json.loads(s)
        print('\nSchema @type:', d.get('@type'))
        print('Headline:', d.get('headline', '')[:80])
        if 'itemListElement' in d:
            items = d['itemListElement']
            print('List elements:', len(items))
            for item in items[:5]:
                print('  Position', item.get('position'), ':', item.get('name', item.get('url', ''))[:50])
        print('All schema keys:', list(d.keys()))
    except Exception as e:
        print('Schema error:', e, s[:100])

# 找 #1 #2 等排名格式
rank_pattern = re.findall(r'(#\d+)\s*[-–—]\s*([^<"\n]{3,60})', content)
print('\nRank patterns found:', len(rank_pattern))
for r, n in rank_pattern[:8]:
    print(' ', r, '-', n.strip()[:50])

# 检查 __NEXT_DATA__
next_data = re.search(r'<script[^>]*id="__NEXT_DATA__"[^>]*>([^<]+)</script>', content)
if next_data:
    print('\n__NEXT_DATA__ found!')
else:
    print('\nNo __NEXT_DATA__')

# 检查文章主体内容
body = re.search(r'<article[^>]*>(.{0,3000})</article>', content, re.DOTALL)
if body:
    print('\nArticle body preview:', body.group(1)[:300])
