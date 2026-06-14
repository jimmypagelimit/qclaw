# -*- coding: utf-8 -*-
import urllib.request, re, json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

url = 'https://stereogum.com/2500947/the-number-ones-the-kid-laroi-justin-biebers-stay/'
req = urllib.request.Request(url, headers=headers)
resp = urllib.request.urlopen(req, timeout=10)
content = resp.read().decode('utf-8', errors='ignore')

match = re.search(r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.+?)</script>', content, re.DOTALL)
if match:
    data = json.loads(match.group(1))
    pp = data['props']['pageProps']
    blocks = pp.get('blocks', [])
    print('Blocks count:', len(blocks))
    print('Block types:', [b.get('__typename', b.get('type', '?')) for b in blocks[:10]])

    # 找包含排名数据的 block
    for i, block in enumerate(blocks):
        bjson = json.dumps(block)
        if any(x in bjson.lower() for x in ['rank', 'number ones', '#1', 'the kid', 'stay']):
            print('\n--- Block', i, '---')
            print('Type:', block.get('__typename', block.get('type')))
            # 打印有用字段
            for k, v in block.items():
                if isinstance(v, str) and len(v) < 200:
                    print(' ', k + ':', v[:80])
                elif isinstance(v, list) and len(v) < 10:
                    print(' ', k + ':', str(v)[:80])
            print()
            if i > 5:
                break
