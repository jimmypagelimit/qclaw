#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓取 RYM piano rock 风格定义 v3 - JS导航+等待"""

import sys
import time
import json
import re
from cloakbrowser import launch

def main():
    print("[1/4] Launching browser...")
    browser = launch(headless=False)
    page = browser.new_page()
    
    # Visit RYM homepage first to pass CF
    print("[2/4] Passing Cloudflare check (35s)...")
    page.goto("https://rateyourmusic.com", wait_until="networkidle", timeout=60000)
    time.sleep(35)
    
    # Use CDP session for JS navigation (avoids Playwright context destruction)
    print("[3/4] Navigating via CDP to /genre/piano+rock/")
    cdp = page.context.browser.new_browser_cdp_session()
    
    # Navigate using CDP
    cdp.send("Page.navigate", {"url": "https://rateyourmusic.com/genre/piano+rock/"})
    time.sleep(30)
    
    # Extract page content
    content = page.content()
    
    # Save raw HTML
    with open(r'C:\Users\qujt\.qclaw\workspace\tasks\rym-expert\_tmp_piano_rock.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  -> Saved HTML ({len(content)} chars)")
    
    # Check if we got the genre page
    if 'piano rock' in content.lower() or 'piano' in content.lower():
        print("  -> Genre page loaded successfully!")
    elif 'cloudflare' in content.lower():
        print("  -> Still on CF challenge!")
        browser.close()
        return
    else:
        print(f"  -> Page title area: {content[:300]}")
    
    # Extract text
    clean = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
    clean = re.sub(r'<style[^>]*>.*?</style>', '', clean, flags=re.DOTALL)
    
    # Get all paragraphs and divs with substantial text
    results = []
    
    paras = re.findall(r'<p[^>]*>(.*?)</p>', clean, re.DOTALL)
    for p in paras:
        text = re.sub(r'<[^>]+>', ' ', p).strip()
        text = re.sub(r'\s+', ' ', text)
        if len(text) > 50:
            results.append(text)
    
    # Also look for definition-like sections
    divs_with_text = re.findall(r'<(?:div|span)[^>]*>([\s\S]*?)</(?:div|span)>', clean)
    
    seen = set()
    unique = []
    for t in results:
        if t not in seen:
            seen.add(t)
            unique.append(t)
    
    print(f"[4/4] Found {len(unique)} text blocks")
    
    output = {
        "genre": "piano rock",
        "url": "https://rateyourmusic.com/genre/piano+rock/",
        "text_blocks": unique
    }
    
    with open(r'C:\Users\qujt\.qclaw\workspace\tasks\rym-expert\_tmp_piano_rock.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    for i, t in enumerate(unique[:15]):
        print(f"  [{i+1}] {t[:200]}...")
    
    browser.close()

if __name__ == "__main__":
    main()
