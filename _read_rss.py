# Read lines 112-125 of RSS-SOURCES.md to find exact content
with open(r'C:\Users\15206\.qclaw\workspace\RSS-SOURCES.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Lines 112-125:")
for i in range(111, min(125, len(lines))):
    print(f"{i+1}: {lines[i].rstrip()}")
