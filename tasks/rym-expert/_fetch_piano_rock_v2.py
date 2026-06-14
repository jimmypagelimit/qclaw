#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓取 RYM piano rock 风格定义 v2"""

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
    print("[2/4] Passing Cloudflare check (30s)...")
    page.goto("https://rateyourmusic.com")
    time.sleep(30)
    
    # Navigate to piano rock genre page via goto with wait_until
    print("[3/4] Navigating to /genre/piano+rock/")
    try:
        page.goto("https://rateyourmusic.com/genre/piano+rock/", wait_until="domcontentloaded", timeout=30000)
    except Exception as e:
        print(f"  goto timeout/error (expected with CF): {e}")
    
    time.sleep(25)
    
    # Extract page content
    content = page.content()
    
    # Save raw HTML
    with open(r'C:\Users\qujt\.qclaw\workspace\tasks\rym-expert\_tmp_piano_rock.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  -> Saved HTML ({len(content)} chars)")
    
    # Check if we got the genre page or a CF block
    if 'cloudflare' in content.lower() or 'challenge-platform' in content.lower():
        print("  -> Still on CF challenge page!")
        browser.close()
        return
    
    if 'piano rock' not in content.lower() and 'piano' not in content.lower():
        print("  -> Page does not contain expected content")
        print(f"  -> First 500 chars: {content[:500]}")
        browser.close()
        return
    
    # Extract text content - look for definition/description areas
    # Remove scripts and styles first
    clean_content = re.sub(r'<script[^>]*>.*?</script>', '', content, flags=re.DOTALL)
    clean_content = re.sub(r'<style[^>]*>.*?</style>', '', clean_content, flags=re.DOTALL)
    
    # Find description-like blocks
    # Try multiple patterns
    results = []
    
    # Pattern 1: Any paragraph with substantial text
    paras = re.findall(r'<p[^>]*>(.*?)</p>', clean_content, re.DOTALL)
    for p in paras:
        text = re.sub(r'<[^>]+>', ' ', p).strip()
        text = re.sub(r'\s+', ' ', text)
        if len(text) > 50:
            results.append(('p', text))
    
    # Pattern 2: divs with text content near genre-related classes
    divs = re.findall(r'<div[^>]*class="[^"]*(?:desc|info|about|text|content|detail|definition|genre|about_genre)[^"]*"[^>]*>(.*?)</div>', clean_content, re.DOTALL)
    for d in divs:
        text = re.sub(r'<[^>]+>', ' ', d).strip()
        text = re.sub(r'\s+', ' ', text)
        if len(text) > 30:
            results.append(('div', text))
    
    # Deduplicate
    seen = set()
    unique = []
    for tag, text in results:
        if text not in seen:
            seen.add(text)
            unique.append((tag, text))
    
    print(f"[4/4] Found {len(unique)} text blocks")
    
    # Save
    output = {
        "genre": "piano rock",
        "url": "https://rateyourmusic.com/genre/piano+rock/",
        "blocks": [{"tag": t, "text": tx} for t, tx in unique]
    }
    
    with open(r'C:\Users\qujt\.qclaw\workspace\tasks\rym-expert\_tmp_piano_rock.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    for i, (tag, text) in enumerate(unique[:10]):
        print(f"  [{i+1}] [{tag}] {text[:150]}...")
    
    browser.close()

if __name__ == "__main__":
    main()
