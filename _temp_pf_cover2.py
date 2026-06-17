#!/usr/bin/env python3
from cloakbrowser import launch
import time, re, urllib.request, os

print("打开 Pitchfork 乐评页...")
browser = launch(headless=False)
page = browser.new_page()
page.goto("https://pitchfork.com/reviews/albums/underscores-u/", timeout=60000)
time.sleep(6)

html = page.content()

# 提取 og:image
m = re.search(r'og:image"[^>]*content="([^"]+)"', html)
if not m:
    m = re.search(r'"image":"(https://media\.pitchfork\.com[^"]+)"', html)
if not m:
    m = re.search(r'(https://media\.pitchfork\.com[^"]+\.(?:jpg|jpeg|png))', html)

if m:
    url = m.group(1).replace('&amp;', '&')
    print(f"封面URL: {url}")

    fname = os.path.join(os.path.dirname(os.path.abspath(__file__)), "album-tracker", "public", "covers", "500-underscores-U.jpg")
    os.makedirs(os.path.dirname(fname), exist_ok=True)
    urllib.request.urlretrieve(url, fname)
    print(f"已保存: {fname}")
else:
    print("未找到封面")
    # 打印一小段html看结构
    print(html[:500])

browser.close()
