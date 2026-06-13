"""Remove remaining tlc default block by line index"""
js_path = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\dist\server.js'
with open(js_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Lines 350-353 (0-indexed: 349-352): remove the tlc default block
new_lines = lines[:349] + lines[353:]
print(f"Before: {len(lines)} lines, After: {len(new_lines)} lines")

count = 0
for line in new_lines:
    if 'total_listen_count' in line:
        count += 1
        print(f"  REMAINING: {line.strip()[:150]}")
print(f"Total remaining: {count}")

with open(js_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print("Written")
