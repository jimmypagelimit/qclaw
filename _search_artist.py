# -*- coding: utf-8 -*-
import time, re
from cloakbrowser import launch

browser = launch(headless=False)
page = browser.new_page()
page.goto('https://rateyourmusic.com/')
time.sleep(20)

# 搜索艺人
print('[1] Searching for artist: Porcelain Stars')
search_box = page.locator("#ui_search_input_main_search").first
search_box.click()
time.sleep(1)
search_box.fill("Porcelain Stars")
time.sleep(1)
search_box.press("Enter")
time.sleep(15)

content = page.content()
with open('rym_search_artist.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f'HTML size: {len(content)} bytes')

if len(content) < 73000:
    print('CF BLOCKED')
    browser.close()
    exit(1)

# 提取艺人链接
artists = re.findall(r'href="(/artist/[^"]+)"[^>]*>([^<]+)<', content)
seen = set()
for l, name in artists[:20]:
    if l not in seen:
        seen.add(l)
        print('ARTIST: ' + l + ' | ' + name)

# 提取专辑链接
albums = re.findall(r'href="(/release/album/[^"]+)"[^>]*>([^<]+)<', content)
seen = set()
for l, name in albums[:20]:
    if l not in seen:
        seen.add(l)
        print('ALBUM: ' + l + ' | ' + name)

print('URL: ' + page.url)
browser.close()