#!/usr/bin/env python3
"""Check if review body is in __PRELOADED_STATE__ or HTML"""
import urllib.request, json, re, sys, ssl
sys.stdout.reconfigure(encoding="utf-8")

ctx = ssl._create_unverified_context()
url = "https://pitchfork.com/reviews/albums/car-seat-headrest-twin-fantasy/"
req = urllib.request.Request(url, headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
})
html = urllib.request.urlopen(req, timeout=15, context=ctx).read().decode("utf-8", errors="replace")
print(f"HTML size: {len(html)}")

# Check PRELOADED_STATE for body
m = re.search(r'window\.__PRELOADED_STATE__\s*=\s*(\{.+?\})\s*;', html, re.DOTALL)
if m:
    data = json.loads(m.group(1))
    review = data.get("transformed", {}).get("review", {})
    body = review.get("body", "")
    # Also check common paths
    for path in ["body", "content", "articleBody", "reviewBody", "displayHed", "lead"]:
        val = review.get(path, "")
        print(f"  review.{path}: {len(str(val))} chars")
    
    # Also check contentStrip
    content = data.get("transformed", {}).get("contentStrip", {})
    print(f"  contentStrip keys: {list(content.keys())[:10]}")
    print(f"  review.body chars: {len(body)}")
    if body:
        print(f"  First 300 chars: {body[:300]}")
else:
    print("No __PRELOADED_STATE__")

# Check HTML for article body
body_patterns = [
    r'<div class="article-content"[^>]*>(.*?)</div>',
    r'<div class="contents"[^>]*>(.*?)</div>',
    r'id="article-body"[^>]*>(.*?)</div>',
]
for pat in body_patterns:
    m = re.search(pat, html, re.DOTALL)
    if m:
        text = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        print(f"\nHTML pattern '{pat[:30]}...': {len(text)} chars")
        print(f"First 200 chars: {text[:200]}")
        break
else:
    # Try splitting by paragraphs
    paras = re.findall(r'<p>([^<]+)</p>', html)
    print(f"\nParagraphs found: {len(paras)}")
    if paras:
        body_text = '\n'.join(paras)
        print(f"Total chars: {len(body_text)}")
        print(f"First 200: {body_text[:200]}")
