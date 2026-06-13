#!/usr/bin/env python3
import sys, time, re, os
from playwright.sync_api import sync_playwright

os.makedirs('rym_genre_test', exist_ok=True)

def get_stealth_args():
    """Get stealth args similar to cloakbrowser"""
    import cloakbrowser
    return cloakbrowser.get_default_stealth_args()

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        args=get_stealth_args() + [
            '--disable-bluetooth',
            '--disable-print-preview',
            '--disable-extensions',
        ],
        timeout=60000
    )
    
    context = browser.new_context(
        locale='en-US',
        timezone_id='America/New_York',
        extra_http_headers={
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': 'https://rateyourmusic.com/',
        }
    )
    page = context.new_page()
    
    print("Step 1: Visiting home page (25s CF wait)...")
    page.goto('https://rateyourmusic.com/', timeout=60000)
    time.sleep(25)
    
    print("Step 2: Navigating to /genre/rock/ via JS...")
    page.evaluate('window.location.href = "/genre/rock/"')
    time.sleep(20)
    
    html = page.content()
    print(f"Page length: {len(html)} bytes")
    
    with open('rym_genre_test/rock_genre_page.html', 'w', encoding='utf-8') as f:
        f.write(html)
    
    title = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
    if title:
        print(f"Title: {title.group(1)}")
    
    if len(html) < 73000:
        print("⚠️ CF challenge page")
    else:
        print("✅ Full page loaded")
        
        # Extract meta description
        meta = re.search(r'<meta[^>]+name="description"[^>]+content="([^"]+)"', html, re.IGNORECASE)
        if meta:
            print(f"\nMeta description:\n{meta.group(1)}")
        
        # Extract article body
        article = re.search(r'<div class="article_body"[^>]*>(.*?)</div>', html, re.IGNORECASE | re.DOTALL)
        if article:
            text = re.sub(r'<[^>]+>', '', article.group(1))
            text = re.sub(r'\s+', ' ', text).strip()
            print(f"\nArticle body ({len(text)} chars):\n{text[:800]}")
        else:
            print("No article_body div found")
    
    browser.close()
    print("\nDone!")