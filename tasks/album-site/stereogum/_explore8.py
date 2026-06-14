# -*- coding: utf-8 -*-
import urllib.request, re, json

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

url = 'https://stereogum.com/2500947/the-number-ones-the-kid-laroi-justin-biebers-stay/'
req = urllib.request.Request(url, headers=headers)
resp = urllib.request.urlopen(req, timeout=10)
content = resp.read().decode('utf-8', errors='ignore')

# 提取 __NEXT_DATA__
match = re.search(r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.+?)</script>', content, re.DOTALL)
if match:
    raw = match.group(1)
    try:
        data = json.loads(raw)
        print('NEXT_DATA keys:', list(data.keys()))
        # 找 pageProps
        pp = data.get('props', {}).get('pageProps', {})
        print('pageProps keys:', list(pp.keys())[:15])
        # 找歌曲排名数据
        if 'songs' in str(pp)[:500]:
            s = json.dumps(pp, indent=2)
            # 找歌曲相关字段
            song_matches = re.findall(r'"(title|name|artist|song|album|ranking|rank|position)":\s*"([^"]{1,60})"', s[:3000])
            for k, v in song_matches[:15]:
                print(k + ':', v)
        # 打印整个 pageProps 的前 500 字
        s = json.dumps(pp, indent=2)
        print('\npageProps preview:', s[:800])
    except Exception as e:
        print('JSON error:', e)
        print('Raw[:200]:', raw[:200])
