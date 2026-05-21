#!/usr/bin/env python3
import sys, re, urllib.request
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

url = "https://music.douban.com/subject/1417420/"
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
resp = urllib.request.urlopen(req, timeout=10)
html = resp.read().decode('utf-8', errors='replace')

# 找封面图
imgs = re.findall(r'src="(https://img\d+\.doubanio\.com/view/subject[^"]+)"', html)
for img in imgs[:5]:
    print(img)
