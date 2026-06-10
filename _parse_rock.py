import re, sys, json
from html import unescape

sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\qujt\.qclaw\workspace\_rym_rock_genre.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Parse the rock genre page for subgenre/style hierarchy
# RYM genre pages have sections: Description, Subgenres, Styles, etc.

# Find all 81 rock-related genres with more context
print("=== RYM Rock Genre Page Analysis ===\n")

# Look for the subgenres section
subgenre_section = re.search(r'(?:subgenres?|Sub-Genres)[^<]*<(?:ul|div)[^>]*>(.*?)</(?:ul|div)>', html, re.DOTALL | re.IGNORECASE)
if subgenre_section:
    print(f"Subgenre section found: {len(subgenre_section.group(1))} chars")
    
# Look for style/section headers to understand organization
headers = re.findall(r'<h[23][^>]*>([^<]+)</h[23]>', html)
print(f"\nPage headers ({len(headers)}):")
for h in headers:
    h = h.strip()
    if h:
        print(f"  - {h}")

# Find all genre links with their surrounding context (parent section)
# Pattern: look for list items or divs containing genre links
print("\n--- All Rock Subgenres ---")
rock_genres = []
for m in re.finditer(r'href="(/genre/([^"]+))"[^>]*>([^<]+)</a>', html):
    url = m.group(1)
    slug = m.group(2)
    name = unescape(m.group(3)).strip()
    
    if 'rock' not in slug.lower():
        continue
    
    # Get context before this link to find parent section
    start = max(0, m.start() - 300)
    context = html[start:m.start()]
    
    # Find nearest header or parent category
    header_match = re.search(r'<h[23][^>]*>([^<]+)</h[23]', context)
    parent = header_match.group(1).strip() if header_match else ""
    
    # Check if it's in a nested list (indicated by <li> depth)
    li_before = context.count('<li')
    
    rock_genres.append({
        'name': name,
        'slug': slug,
        'url': url,
        'parent_section': parent,
        'nesting': li_before
    })

# Deduplicate by slug
seen = set()
unique = []
for g in rock_genres:
    if g['slug'] not in seen:
        seen.add(g['slug'])
        unique.append(g)

print(f"Total unique rock subgenres: {len(unique)}")
for g in unique:
    extra = f" [section: {g['parent_section']}]" if g['parent_section'] else ""
    print(f"  {g['name']}{extra}")

# Save
with open(r'C:\Users\qujt\.qclaw\workspace\_rym_rock_subgenres.json', 'w', encoding='utf-8') as f:
    json.dump(unique, f, ensure_ascii=False, indent=2)

# Also get non-rock genres that appear on this page (related genres)
print("\n--- Related Non-Rock Genres on this page ---")
other_genres = []
for m in re.finditer(r'href="(/genre/([^"]+))"[^>]*>([^<]+)</a>', html):
    slug = m.group(2)
    name = unescape(m.group(3)).strip()
    if 'rock' in slug.lower() or slug in seen:
        continue
    if name and len(name) < 60:
        other_genres.append((slug, name))

other_unique = sorted(set(other_genres), key=lambda x: x[0])
print(f"Found {len(other_unique)} related genres:")
for slug, name in other_unique[:30]:
    print(f"  {slug} -> {name}")