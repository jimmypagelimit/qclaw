path = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\dist\server.js'
with open(path, 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines, 1):
    if 'total_listen_count' in line:
        idx = line.find('total_listen_count')
        start = max(0, i-2)
        end = min(len(lines)+1, i+3)
        print(f'=== AROUND L{i} ===')
        for j in range(start, end):
            prefix = '> ' if j == i else '  '
            print(f'{prefix}L{j}: {lines[j-1].rstrip()[:200]}')
        print()
print(f'Total: {sum(1 for l in lines if "total_listen_count" in l)}')
