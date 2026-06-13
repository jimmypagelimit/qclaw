#!/usr/bin/env python3
import sys, time, re, os
from playwright.sync_api import sync_playwright

os.makedirs('rym_genre_test', exist_ok=True)

def get_stealth_args():
    import cloakbrowser
    return cloakbrowser.get_default_stealth_args()

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        args=get_stealth_args() + ['--disable-bluetooth', '--disable-print-preview'],
        timeout=60000
    )
    
    context = browser.new_context(
        locale='en-US',
        timezone_id='America/New_York',
        extra_http_headers={'Accept-Language': 'en-US,en;q=0.9'}
    )
    page = context.new_page()
    
    print("Step 1: Visiting home page...")
    page.goto('https://rateyourmusic.com/', timeout=60000)
    
    # Poll until CF challenge is done (page size > 73000)
    print("Waiting for CF challenge to complete...")
    for i in range(30):
        time.sleep(2)
        html = page.content()
        if len(html) > 73000 and 'cloudflare' not in html.lower():
            print(f"CF passed after {2*(i+1)}s (page size: {len(html)})")
            break
        print(f"  Check {i+1}/30: {len(html)} bytes", flush=True)
    else:
        print("CF challenge did not complete in time")
        html = page.content()
        with open('rym_genre_test/cf_page.html', 'w', encoding='utf-8') as f:
            f.write(html)
        browser.close()
        sys.exit(1)
    
    print("Step 2: Navigating to /genre/rock/ via JS...")
    page.evaluate('window.location.href = "/genre/rock/"')
    time.sleep(15)
    
    html = page.content()
    print(f"Genre page size: {len(html)} bytes")
    
    with open('rym_genre_test/rock_genre_page.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    title = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
    if title:
        print(f"Title: {title.group(1)}")
    
    if len(html) < 73000:
        print("Still CF or short page")
    else:
        # Extract meta description
        meta = re.search(r'<meta[^>]+name="description"[^>]+content="([^"]+)"', html, re.IGNORECASE)
        if meta:
            print(f"\nMeta description:\n{meta.group(1)}")
        
        # Extract article body
        article = re.search(r'<div class="article_body"[^>]*>(.*?)</div>', html, re.IGNORECASE | re.DOTALL)
        if article:
            text = re.sub(r'<[^>]+>', '', article.group(1))
            text = re.sub(r'\s+', ' ', text).strip()
            print(f"\nArticle body ({len(text)} chars):\n{text[:1000]}")
        else:
            print("No article_body div found")
    
    browser.close()
    print("\nDone!")