import sqlite3, os
from collections import Counter

db = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
c = db.cursor()

# Get all paths
c.execute("SELECT lyrics_text_path FROM tracks WHERE lyrics_text_path IS NOT NULL AND lyrics_text_path != ''")
paths = [r[0] for r in c.fetchall()]

# Classify
by_ext = Counter()
by_dir = Counter()
broken_samples = []

for p in paths:
    ext = os.path.splitext(p)[1] if '.' in p else '(no ext)'
    d = os.path.dirname(p)
    exists = os.path.exists(p)
    if not exists:
        by_ext[ext] += 1
        by_dir[d] += 1
        if len(broken_samples) < 8:
            broken_samples.append((p, exists))

print(f'总路径数: {len(paths)}')
print(f'文件存在: {sum(1 for p in paths if os.path.exists(p))}')
print(f'文件不存在: {sum(1 for p in paths if not os.path.exists(p))}')

print(f'\nBroken paths by extension:')
for ext, cnt in by_ext.most_common():
    print(f'  {repr(ext)}: {cnt}')

print(f'\nBroken paths by directory:')
for d, cnt in by_dir.most_common(8):
    print(f'  {d}: {cnt}')

print(f'\nSample broken paths:')
for p, exists in broken_samples:
    print(f'  exists={exists} {repr(p[:120])}')

# Count how many have no useful extension
no_ext_count = sum(1 for p in paths if not os.path.exists(p) and '.' not in os.path.basename(p))
print(f'\nBroken with no file extension: {no_ext_count}')

# Check broken paths that look like GBK garbage
import re
garbled = [p for p in paths if not os.path.exists(p) and not p.endswith('.txt') and not p.endswith('.lrc')]
print(f'Broken paths not ending in .txt or .lrc: {len(garbled)}')
for p in garbled[:5]:
    print(f'  {repr(p[:100])}')

db.close()
