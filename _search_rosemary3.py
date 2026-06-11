# -*- coding: utf-8 -*-
import time, re
from cloakbrowser import launch

browser = launch(headless=False)
page = browser.new_page()
page.goto('https://rateyourmusic.com/')
time.sleep(20)

# 使用搜索框
print('[1] Searching via search box...')
search_box = page.locator("#ui_search_input_main_search").first
search_box.click()
time.sleep(1)
search_box.fill("Rosemary Porcelain Stars")
time.sleep(1)
search_box.press("Enter")
time.sleep(15)

content = page.content()
with open('rym_search3.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f'HTML size: {len(content)} bytes')

if len(content) < 73000:
    print('CF BLOCKED')
    browser.close()
    exit(1)

# Find all release links and album info
albums = re.findall(r'href="(/release/album/[^"]+)"[^>]*>([^<]+)<', content)
seen = set()
for l, name in albums[:30]:
    if l not in seen:
        seen.add(l)
        print(l + ' | ' + name)

# Also print current URL
print('Current URL: ' + page.url)

browser.close()
