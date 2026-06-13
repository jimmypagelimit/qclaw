import re

f = open('rym_genre_test/rock_genre_page.html', 'r', encoding='utf-8')
c = f.read()

# Find meta description
meta = re.search(r'<meta[^>]+name="description"[^>]+content="([^"]+)"', c, re.I)
print('META:', meta.group(1) if meta else 'none')

# Find any meaningful text content areas
# Look for divs with actual text
text_blocks = re.findall(r'<div class="[^"]*"[^>]*>(.*?)</div>', c, re.I | re.S)
meaningful = []
for b in text_blocks:
    t = re.sub(r'<[^>]+>', '', b)
    t = re.sub(r'\s+', ' ', t).strip()
    if len(t) > 200:
        meaningful.append((len(t), t[:400]))

meaningful.sort(reverse=True)
print(f"\nFound {len(meaningful)} meaningful text blocks (>200 chars)")
for l, t in meaningful[:5]:
    print(f"\n--- {l} chars ---")
    print(t)