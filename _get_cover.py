# -*- coding: utf-8 -*-
"""用 CloakBrowser 打开 Spotify 专辑页截图，找封面 URL"""
import time, re
from cloakbrowser import launch

browser = launch(headless=False)
page = browser.new_page()
page.goto('https://open.spotify.com/album/06kkKhg5kSJEw416kwrq2C')
time.sleep(15)

content = page.content()
with open('spotify_album.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('HTML size:', len(content))

# 找封面 URL
urls = re.findall(r'https://i\.scdn\.co/image/[^\s"\'&]+', content)
for u in urls[:5]:
    print(u)

browser.close()