#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓取 RYM piano rock 风格定义 v5 - 长等待"""

import sys
import time
import json
import re
from cloakbrowser import launch

def main():
    print("[1/5] Launching browser...")
    browser = launch(headless=False)
    page = browser.new_page()
    
    # Visit RYM homepage first - don't wait for load event
    print("[2/5] Navigating to RYM homepage...")
    try:
        page.goto("https://rateyourmusic.com", timeout=15000)
    except:
        pass  # CF redirects expected
    
    # Wait longer for CF
    print("[3/5] Waiting 50s for CF challenge...")
    time.sleep(50)
    
    # Check if we're past CF
    # Retry content() as CF may be navigating
    for attempt in range(5):
        try:
            time.sleep(3)
            content = page.content()
            break
        except:
            print(f"  -> content() retry {attempt+1}...")
            continue
    else:
        content = ''
        print("  -> Could not get page content")
    
    if content and 'cloudflare' in content.lower() and 'challenge' in content.lower():
        print("  -> Still on CF, waiting 30s more...")
        time.sleep(30)
        for attempt in range(5):
            try:
                time.sleep(3)
                content = page.content()
                break
            except:
                continue
    
    if content and 'cloudflare' in content.lower() and 'challenge' in content.lower():
        print("  -> CF still blocking. Checking URL...")
        print(f"  -> URL: {page.url}")
        # Try clicking the turnstile checkbox
        try:
            checkbox = page.locator('#cf-chl-widget-iur0c_response')
            if checkbox:
                print("  -> Found turnstile widget")
        except:
            pass
        browser.close()
        print("  -> Failed to pass CF")
        return
    
    print(f"  -> Page loaded: {page.url}")
    
    # Navigate to genre page via JS
    print("[4/5] Navigating to /genre/piano+rock/")
    try:
        page.evaluate("window.location.href = '/genre/piano+rock/'")
    except:
        pass  # Context destroyed by navigation, expected
    
    time.sleep(30)
    
    # Check URL
    try:
        current_url = page.url
        print(f"  -> Current URL: {current_url}")
    except:
        pass
    
    for attempt in range(5):
        try:
            time.sleep(3)
            content = page.content()
            break
        except:
            continue
    else:
        content = ''
    
    with open(r'C:\Users\qujt\.qclaw\workspace\tasks\rym-expert\_tmp_piano_rock_v5.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  -> Saved HTML ({len(content)} chars)")
    
    # Check if genre page loaded
    if 'piano' in content.lower():
        print("  -> Genre page loaded!")
    else:
        print("  -> Content check failed")
        title_match = re.search(r'<title>(.*?)</title>', content, re.DOTALL)
        if title_match:
            print(f"  -> Title: {title_match.group(1)[:100]}")
    
    # Extract text
    clean = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
    clean = re.sub(r'<style[^>]*>.*?</style>', '', clean, flags=re.DOTALL)
    
    results = []
    paras = re.findall(r'<p[^>]*>(.*?)</p>', clean, re.DOTALL)
    for p in paras:
        text = re.sub(r'<[^>]+>', ' ', p).strip()
        text = re.sub(r'\s+', ' ', text)
        if len(text) > 40:
            results.append(text)
    
    seen = set()
    unique = []
    for t in results:
        if t not in seen:
            seen.add(t)
            unique.append(t)
    
    print(f"[5/5] Found {len(unique)} text blocks")
    
    output = {
        "genre": "piano rock",
        "url": "https://rateyourmusic.com/genre/piano+rock/",
        "text_blocks": unique
    }
    
    with open(r'C:\Users\qujt\.qclaw\workspace\tasks\rym-expert\_tmp_piano_rock_v5.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    for i, t in enumerate(unique[:15]):
        print(f"  [{i+1}] {t[:200]}...")
    
    browser.close()

if __name__ == "__main__":
    main()
