# -*- coding: utf-8 -*-
import time, re
from cloakbrowser import launch

browser = launch(headless=False)
page = browser.new_page()
page.goto('https://rateyourmusic.com/', wait_until='networkidle')
time.sleep(20)

# 搜索
search_url = 'https://rateyourmusic.com/search?searchterm=Rosemary+Porcelain+Stars'
page.goto(search_url, wait_until='networkidle')
time.sleep(12)

content = page.content()
with open('rym_search2.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f'HTML size: {len(content)} bytes')

# CF check
if len(content) < 73000:
    print('CF BLOCKED')
    browser.close()
    exit(1)

# Find all release links
links = re.findall(r'href="(/release/album/[^"]+)"', content)
seen = set()
for l in links[:20]:
    if l not in seen:
        seen.add(l)
        print(l)

# Find album names near links
albums = re.findall(r'class="release".*?href="(/release/album/[^"]+)".*?class="artist">([^<]+)<.*?class="album">([^<]+)<', content, re.DOTALL)
for album_url, artist, album in albums[:10]:
    print(f'{album_url} | {artist} | {album}')

browser.close()
