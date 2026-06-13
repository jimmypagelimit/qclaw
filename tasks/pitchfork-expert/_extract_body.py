#!/usr/bin/env python3
"""Extract review body from Pitchfork review page.
Uses same HTTP pattern as pf_scraper.py (which works)."""
import urllib.request, json, re, ssl, sys
sys.stdout.reconfigure(encoding="utf-8")

ctx = ssl._create_unverified_context()

def fetch_html(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml",
    })
    with urllib.request.urlopen(req, timeout=20, context=ctx) as resp:
        return resp.read().decode("utf-8", errors="replace")

# Test with a BNM review: Twin Fantasy (8.6)
url = "https://pitchfork.com/reviews/albums/car-seat-headrest-twin-fantasy/"
print(f"Fetching: {url}")
html = fetch_html(url)
print(f"HTML size: {len(html)} bytes")

# Try __PRELOADED_STATE__ first
m = re.search(r'window\.__PRELOADED_STATE__\s*=\s*(\{.*?\})\s*;', html, re.DOTALL)
if m:
    print("Found __PRELOADED_STATE__")
    try:
        data = json.loads(m.group(1))
        # Dump all top-level keys
        print(f"  Top keys: {list(data.keys())}")
        transformed = data.get("transformed", {})
        print(f"  transformed keys: {list(transformed.keys())}")
        review = transformed.get("review", {})
        print(f"  review keys: {list(review.keys())}")
        # Look for body-like fields
        body = review.get('body', '')
        if body:
            print(f"\n*** FOUND review['body']: {len(body)} chars ***")
            print(f"First 500 chars: {body[:500]}")
        else:
            print("  review['body'] is empty")
        for k, v in review.items():
            if isinstance(v, str) and len(v) > 500 and k != 'body':
                print(f"  review['{k}']: {len(v)} chars, first 150: {v[:150]}")
    except Exception as e:
        print(f"  JSON parse error: {e}")
else:
    print("No __PRELOADED_STATE__ found")

# Try HTML patterns for article body
print("\n--- HTML body patterns ---")
# Pattern 1: <div class="article-content">
m = re.search(r'<div class="article-content"[^>]*>(.*?)</div>\s*</div>', html, re.DOTALL)
if m:
    text = re.sub(r'<[^>]+>', '', m.group(1))
    print(f"Pattern 'article-content': {len(text)} chars")
    print(f"  First 300: {text[:300]}")

# Pattern 2: all <p> tags (filter out nav/header junk)
paras = re.findall(r'<p[^>]*>([^<]*(?:<[^>]+>[^<]*)*)</p>', html)
# Filter: reasonable length, no script/nav classes
real_paras = []
for p in paras:
    clean = re.sub(r'<[^>]+>', '', p).strip()
    if len(clean) > 50 and not re.match(r'^(Facebook|Twitter|Sign up|Log in)', clean):
        real_paras.append(clean)
print(f"\nFound {len(real_paras)} substantial <p> tags")
if real_paras:
    print(f"First para: {real_paras[0][:300]}")
    print(f"Total chars: {sum(len(p) for p in real_paras)}")
