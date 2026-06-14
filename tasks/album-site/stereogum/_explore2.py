# -*- coding: utf-8 -*-
import urllib.request, re, json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# 抓单篇 music 页面，分析 __PRELOADED_STATE__
url = 'https://stereogum.com/2502199/la-securites-bingo-is-the-art-punk-party-record-your-weekend-needs/music/'
req = urllib.request.Request(url, headers=headers)
resp = urllib.request.urlopen(req, timeout=10)
content = resp.read().decode('utf-8', errors='ignore')

# 找 __PRELOADED_STATE__
match = re.search(r'__PRELOADED_STATE__\s*=\s*({.*?})\s*;?\s*$', content, re.MULTILINE | re.DOTALL)
if not match:
    match = re.search(r'window\.__PRELOADED_STATE__\s*=\s*(.+)', content)
if match:
    raw = match.group(1).strip()
    # 找到 JSON 结束位置
    brace_count = 0
    end = 0
    in_str = False
    escape = False
    for i, c in enumerate(raw):
        if escape:
            escape = False
            continue
        if c == '\\':
            escape = True
            continue
        if c == '"' and not escape:
            in_str = not in_str
        if not in_str:
            if c == '{':
                brace_count += 1
            elif c == '}':
                brace_count -= 1
                if brace_count == 0:
                    end = i + 1
                    break
    try:
        data = json.loads(raw[:end])
        print('JSON parsed OK, keys:', list(data.keys())[:10])
        # 找 post 数据
        if 'post' in data:
            post = data['post']
            print('\nPost keys:', list(post.keys()))
            print('Title:', post.get('title', 'N/A')[:60])
            print('Type:', post.get('type', 'N/A'))
            print('Artist:', post.get('artist', 'N/A'))
            print('Album:', post.get('album', 'N/A'))
            print('Rating:', post.get('rating', 'N/A'))
            print('Genres:', post.get('genres', []))
            print('Label:', post.get('label', 'N/A'))
        if 'album' in str(data)[:500]:
            # 搜索 album 相关字段
            s = json.dumps(data, indent=2)
            alb_keys = re.findall(r'"(album|artist|rating|genre|label|year|style|type)":\s*"([^"]{1,60})"', s[:5000])
            for k, v in alb_keys[:15]:
                print(k + ':', v)
    except Exception as e:
        print('JSON parse error:', e)
        print('Raw[:200]:', raw[:200])
else:
    print('No __PRELOADED_STATE__ found')
    print('Looking for schema.org instead...')
    schema = re.search(r'application/ld\+json[^>]*>(.{0,2000})', content)
    if schema:
        print('Schema found:', schema.group(1)[:300])
