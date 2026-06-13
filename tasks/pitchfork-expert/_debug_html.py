"""Find album list data in the best-of page HTML"""
import subprocess, json, re

html = subprocess.run(
    ["curl", "-k", "-s", "-L", "https://pitchfork.com/best/albums/2024/"],
    capture_output=True, text=False, timeout=20
).stdout.decode("utf-8", errors="replace")

# Check for SSR content: look for album titles embedded in HTML
# Try various patterns

# 1. Look for o-ReviewListItem or similar CSS class wrappers
reviews = re.findall(r'<div[^>]*class="[^"]*review[^"]*"[^>]*>.*?<a[^>]*href="(/reviews/albums/[^"]+)"[^>]*>(.*?)</a>', html, re.DOTALL)
print(f"Method 1 (review+link): {len(reviews)}")
if reviews:
    for href, text in reviews[:5]:
        print(f"  {href}: {re.sub(r'<[^>]+>', '', text).strip()[:80]}")

# 2. Look for any <a> with /reviews/albums/ in best-of page
links = set(re.findall(r'href="(https://pitchfork\.com/reviews/albums/[^"]+)"', html))
print(f"\nMethod 2 (direct links): {len(links)}")
for l in list(links)[:5]:
    name = l.split("/")[-1].replace("-", " ").title()
    print(f"  {l}: {name}")

# 3. Look for specific list item patterns
items = re.findall(r'<a[^>]*class="[^"]*"[^>]*href="(/reviews/albums/[^"]+)"[^>]*>\s*<[^>]+>\s*([^<]+)', html)
print(f"\nMethod 3 (link with title): {len(items)}")
for href, title in items[:10]:
    print(f"  {href}: {title.strip()[:60]}")

# 4. Look for JSON-LD
jsonld = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
print(f"\nMethod 4 (JSON-LD): {len(jsonld)}")
for i, block in enumerate(jsonld[:3]):
    try:
        d = json.loads(block)
        print(f"  Block {i}: type={d.get('@type')} keys={list(d.keys())[:10]}")
        if d.get("@type") == "ItemList":
            items = d.get("itemListElement", [])
            print(f"    Items: {len(items)}")
            for item in items[:5]:
                print(f"      {item.get('name', '?')[:60]} -> {item.get('url', '')}")
    except:
        pass

# 5. Save a snippet for manual inspection
with open(r'C:\Users\qujt\.qclaw\workspace\tasks\pitchfork-expert\data\pf_best_2024_snippet.html', 'w', encoding='utf-8') as f:
    # Find the first mention of "Best New" or review
    idx = html.lower().find('class="best')
    if idx < 0:
        idx = max(0, html.lower().find('review') - 1000)
    f.write(html[idx:idx+20000])
print("\nSnippet saved for manual inspection")
