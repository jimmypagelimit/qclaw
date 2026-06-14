#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓取 RYM piano rock 风格定义 v4 - evaluate+catch"""

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
    try:
        page.goto("https://rateyourmusic.com", timeout=15000)
    except:
        pass  # CF challenge redirects, expected
    time.sleep(40)
    
    # Navigate via JS - catch the expected error
    print("[3/4] Navigating to /genre/piano+rock/")
    try:
        page.evaluate("window.location.href = '/genre/piano+rock/'")
    except Exception as e:
        print(f"  -> Navigation error (expected): {str(e)[:80]}")
    
    # Wait for new page to load
    time.sleep(30)
    
    content = page.content()
    
    with open(r'C:\Users\qujt\.qclaw\workspace\tasks\rym-expert\_tmp_piano_rock.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  -> Saved HTML ({len(content)} chars)")
    
    # Check page
    lower = content.lower()
    if 'piano rock' in lower:
        print("  -> Genre page loaded!")
    elif 'piano' in lower:
        print("  -> Page has 'piano' content")
    else:
        print(f"  -> Check: title={re.search(r'<title>(.*?)</title>', content, re.DOTALL)}")
    
    # Extract text
    clean = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
    clean = re.sub(r'<style[^>]*>.*?</style>', '', clean, flags=re.DOTALL)
    
    results = []
    paras = re.findall(r'<p[^>]*>(.*?)</p>', clean, re.DOTALL)
    for p in paras:
        text = re.sub(r'<[^>]+>', ' ', p).strip()
        text = re.sub(r'\s+', ' ', text)
        if len(text) > 50:
            results.append(text)
    
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
