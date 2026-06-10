import re, sys, json
from html import unescape

sys.stdout.reconfigure(encoding='utf-8')

with open(r'C:\Users\qujt\.qclaw\workspace\_rym_genres_expanded.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Step 1: Extract only the genre link lines (much smaller)
lines = html.split('\n')
genre_lines = []
for line in lines:
    if '/genre/' in line and 'href=' in line:
        genre_lines.append(line)

print(f"Lines with /genre/: {len(genre_lines)}")

# Step 2: Parse each line for slug + name + position
genre_data = []
for i, line in enumerate(genre_lines):
    m = re.search(r'href="/genre/([^"]+)"[^>]*>([^<]+)</a>', line)
    if m:
        slug = m.group(1)
        name = unescape(m.group(2)).strip()
        if name and len(name) < 100:
            # Find position in original HTML
            pos = html.find(line)
            if pos >= 0:
                genre_data.append((pos, slug, name))

print(f"Parsed entries: {len(genre_data)}")

# Step 3: Sort by position and deduplicate
genre_data.sort(key=lambda x: x[0])
seen_pos = set()
unique = []
for item in genre_data:
    if item[0] not in seen_pos:
        seen_pos.add(item[0])
        unique.append(item)

print(f"Unique sorted entries: {len(unique)}")

# Step 4: Build tree by <li> depth
results = []
for pos, slug, name in unique:
    snippet = html[:pos]
    opens = snippet.count('<li')
    closes = snippet.count('</li>')
    depth = max(0, opens - closes - 1)
    results.append({'name': name, 'slug': slug, 'depth': depth})

# Step 5: Build nested tree
def build_tree(flat):
    root = []
    stack = []
    for item in flat:
        node = {**item, 'children': []}
        d = item['depth']
        while stack and stack[-1][1] >= d:
            stack.pop()
        if stack:
            stack[-1][0]['children'].append(node)
        else:
            root.append(node)
        stack.append((node, d))
    return root

tree = build_tree(results)

def count_nodes(nodes):
    return sum(1 + count_nodes(n['children']) for n in nodes)

def find_node(nodes, slug):
    for n in nodes:
        if n['slug'] == slug: return n
        r = find_node(n['children'], slug)
        if r: return r
    return None

def print_tree(n, indent=0):
    prefix = ("│   " * indent) + ("├─ " if indent > 0 else "")
    print(f"{prefix}{n['name']}")
    for ch in n['children']:
        print_tree(ch, indent + 1)

total = count_nodes(tree)
print(f"\n✅ Total genres: {total}")

# Top-level summary
print(f"\n{'='*60}")
print(f"RYM COMPLETE GENRE TREE — {len(tree)} top-level categories")
print(f"{'='*60}")
for n in tree:
    cc = count_nodes(n['children'])
    print(f"  🎵 {n['name']} ({n['slug']}) [{cc} subgenres]")

# ROCK SUBTREE
rock = find_node(tree, 'rock')
if rock:
    rc = count_nodes([rock])
    print(f"\n{'='*60}")
    print(f"🎸 ROCK STYLE TREE — {rc} genres total")
    print(f"{'='*60}")
    print_tree(rock)
    
    with open(r'C:\Users\qujt\.qclaw\workspace\_rym_rock_tree.json', 'w', encoding='utf-8') as f:
        json.dump(rock, f, ensure_ascii=False, indent=2)
    print(f"\n💾 Saved _rym_rock_tree.json")
else:
    print("\n⚠️ Rock not found at top level")
    # Search all nodes
    def search_all(nodes, term='rock'):
        for n in nodes:
            if term in n['slug'].lower():
                print(f"  Found: {n['name']} ({n['slug']}) depth={n.get('depth','?')}")
            search_all(n['children'], term)
    search_all(tree)

# Save full tree
with open(r'C:\Users\qujt\.qclaw\workspace\_rym_full_genre_tree.json', 'w', encoding='utf-8') as f:
    json.dump(tree, f, ensure_ascii=False, indent=2)
print(f"💾 Saved _rym_full_genre_tree.json")