import json

with open(r'C:\Users\qujt\.qclaw\workspace\_rym_rock_tree.json', 'r', encoding='utf-8') as f:
    rock = json.load(f)

def count(n):
    return 1 + sum(count(c) for c in n.get('children', []))

def print_tree(n, indent=0):
    prefix = "│   " * indent + ("├─ " if indent > 0 else "")
    name = n.get('name', '?')
    print(f"{prefix}{name}")
    for c in n.get('children', []):
        print_tree(c, indent + 1)

total = count(rock)
print(f"ROCK STYLE TREE -- {total} genres total")
print("=" * 60)
print_tree(rock)
