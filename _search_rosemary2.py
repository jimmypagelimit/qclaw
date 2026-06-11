# -*- coding: utf-8 -*-
import time, re
from cloakbrowser import launch

browser = launch(headless=False)
page = browser.new_page()
page.goto('https://rateyourmusic.com/')
time.sleep(20)

# 直接导航到搜索页
page.goto('https://rateyourmusic.com/search?searchterm=Rosemary+Porcelain+Stars')
time.sleep(12)

content = page.content()
with open('rym_search2.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f'HTML size: {len(content)} bytes')

if len(content) < 73000:
    print('CF BLOCKED')
    browser.close()
    exit(1)

# 提取专辑链接
links = re.findall(r'href="(/release/album/[^"]+)"', content)
seen = set()
for l in links[:30]:
    if l not in seen:
        seen.add(l)
        print(l)

browser.close()
