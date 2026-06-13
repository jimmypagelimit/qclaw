#!/usr/bin/env python3
import sys, time, re, os
from cloakbrowser import launch

url = 'https://rateyourmusic.com/genre/rock/'
os.makedirs('rym_genre_test', exist_ok=True)

print("Launching browser...")
with launch(headless=False, timeout=120000) as browser:
    print("Browser launched!")
    page = browser.new_page()
    
    print("Visiting home page...")
    page.goto('https://rateyourmusic.com/', timeout=60000, wait_until='domcontentloaded')
    
    # Poll until CF is done (page size > 73000)
    print("Waiting for CF challenge...")
    for i in range(40):
        time.sleep(2)
        try:
            html = page.content()
        except:
            continue
        if len(html) > 73000 and 'cloudflare' not in html.lower():
            print(f"CF passed after {2*(i+1)}s (page size: {len(html)})")
            break
        if i % 5 == 4:
            print(f"  Check {i+1}/40: {len(html)} bytes", flush=True)
    else:
        print("CF challenge did not complete")
        html = page.content()
        with open('rym_genre_test/cf_page.html', 'w', encoding='utf-8') as f:
            f.write(html)
        sys.exit(1)
    
    print("Navigating to genre page via JS...")
    page.evaluate('window.location.href = "/genre/rock/"')
    
    # Poll until genre page loads
    for i in range(20):
        time.sleep(2)
        try:
            html = page.content()
        except:
            continue
        if len(html) > 73000:
            print(f"Genre page loaded after {2*(i+1)}s (size: {len(html)})")
            break
        if i % 5 == 4:
            print(f"  Genre check {i+1}/20: {len(html)} bytes", flush=True)
    else:
        print("Genre page load timeout")
        html = page.content()
    
    with open('rym_genre_test/rock_genre_page.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    # Extract title
    title = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
    if title:
        print(f"Title: {title.group(1)}")
    
    # Extract meta description
    meta = re.search(r'<meta[^>]+name="description"[^>]+content="([^"]+)"', html, re.IGNORECASE)
    if meta:
        print(f"\nMeta description:\n{meta.group(1)}")
    
    # Extract article body
    article = re.search(r'<div class="article_body"[^>]*>(.*?)</div>', html, re.IGNORECASE | re.DOTALL)
    if article:
        text = re.sub(r'<[^>]+>', '', article.group(1))
        text = re.sub(r'\s+', ' ', text).strip()
        print(f"\nArticle body ({len(text)} chars):\n{text[:1500]}")
    else:
        print("No article_body div found")

print("Done!")