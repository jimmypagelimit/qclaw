#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""抓取 RYM piano rock 风格定义"""

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
    
    # Navigate to piano rock genre page via JS
    print("[3/4] Navigating to /genre/piano+rock/")
    page.evaluate("window.location.href = '/genre/piano+rock/'")
    time.sleep(25)
    
    # Extract page content
    content = page.content()
    
    # Save raw HTML for inspection
    with open(r'C:\Users\qujt\.qclaw\workspace\tasks\rym-expert\_tmp_piano_rock.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  -> Saved HTML ({len(content)} chars)")
    
    # Extract description/definition text
    # RYM genre pages typically have a description section
    # Look for definition paragraphs
    desc_patterns = [
        r'<div class="genre_description[^"]*">(.*?)</div>',
        r'<p class="genre_desc[^"]*">(.*?)</p>',
        r'<div class="profile_genre_description[^"]*">(.*?)</div>',
        r'class="genre_info[^"]*"[^>]*>(.*?)</div>',
        r'class="breadcrumb_detail"[^>]*>(.*?)</',
    ]
    
    descriptions = []
    for pattern in desc_patterns:
        matches = re.findall(pattern, content, re.DOTALL)
        for m in matches:
            clean = re.sub(r'<[^>]+>', ' ', m).strip()
            clean = re.sub(r'\s+', ' ', clean)
            if len(clean) > 20:
                descriptions.append(clean)
    
    # Also try to find any text blocks near "piano rock" heading
    # Look for the main content area
    main_match = re.search(r'<div[^>]*class="[^"]*genre[^"]*"[^>]*>(.*?)</div>\s*</div>', content, re.DOTALL)
    
    # Extract all text between genre-related elements
    text_blocks = re.findall(r'<(?:p|div|span)[^>]*class="[^"]*(?:desc|info|about|text|content|detail)[^"]*"[^>]*>(.*?)</(?:p|div|span)>', content, re.DOTALL)
    for tb in text_blocks:
        clean = re.sub(r'<[^>]+>', ' ', tb).strip()
        clean = re.sub(r'\s+', ' ', clean)
        if len(clean) > 30:
            descriptions.append(clean)
    
    # Save results
    result = {
        "genre": "piano rock",
        "descriptions": descriptions,
        "html_saved": True
    }
    
    with open(r'C:\Users\qujt\.qclaw\workspace\tasks\rym-expert\_tmp_piano_rock.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"[4/4] Found {len(descriptions)} description blocks")
    for i, d in enumerate(descriptions):
        print(f"  [{i+1}] {d[:200]}...")
    
    browser.close()

if __name__ == "__main__":
    main()
