import re, os
path = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\package.json'
with open(path, 'r', encoding='utf-8') as f:
    pkg = f.read()
m = re.search(r'"build":\s*"([^"]+)"', pkg)
print('build:', m.group(1) if m else 'NOT FOUND')
m = re.search(r'"dev":\s*"([^"]+)"', pkg)
print('dev:', m.group(1) if m else 'NOT FOUND')
