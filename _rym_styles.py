import cloakbrowser, time, re, sys

sys.stdout.reconfigure(encoding='utf-8')

b = cloakbrowser.launch(headless=False)
ctx = b.new_context()
page = ctx.new_page()

# Use goto without wait_until, let CF challenge complete naturally
page.goto('https://rateyourmusic.com/')
print('Main page loading, waiting 25s for CF...')
time.sleep(25)

title = page.evaluate('document.title')
print(f'Title: {repr(title)}')

if '请稍候' in title:
    print('CF not passed, waiting more...')
    time.sleep(15)
    title = page.evaluate('document.title')
    print(f'Title after wait: {repr(title)}')

# Navigate to genre page
page.goto('https://rateyourmusic.com/~rstyles')
print('Genre page loading, waiting 15s...')
time.sleep(15)

title2 = page.evaluate('document.title')
print(f'Genre title: {repr(title2)}')

html = page.evaluate('document.documentElement.outerHTML')
print(f'HTML: {len(html)} chars')

# Find all links
all_links = re.findall(r'href=["\']([^"\']+)["\']', html)
print(f'Total links: {len(all_links)}')

# Save HTML for inspection
with open(r'C:\Users\qujt\.qclaw\workspace\_rym_genres.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('Saved to _rym_genres.html')

page.context.browser.close()
print('Done')