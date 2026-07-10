"""Reconcile lyrics_text_path: fix relative paths, clear broken ones"""
import sqlite3, os

DB_PATH = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
LYRICS_BASE = r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics'

db = sqlite3.connect(DB_PATH)
c = db.cursor()

# Get all non-empty paths
c.execute("SELECT id, lyrics_text_path FROM tracks WHERE lyrics_text_path IS NOT NULL AND lyrics_text_path != ''")
rows = c.fetchall()

fix_rel_to_full = []    # id -> new full path
set_to_null = []         # ids
remaining_rel = []       # relative paths where file also doesn't exist at base

for tid, path in rows:
    if os.path.exists(path):
        # Already a valid full path
        continue
    
    # Try prepending base_dir
    full_path = os.path.join(LYRICS_BASE, path)
    if os.path.exists(full_path):
        fix_rel_to_full.append((tid, full_path))
    else:
        # Check if it's a relative path with wrong structure
        # Some are like "lyrics/嘎调..." path
        set_to_null.append(tid)
        remaining_rel.append((tid, path))

# Fix empty-string entries
c.execute("SELECT id FROM tracks WHERE lyrics_text_path = ''")
empty_ids = [r[0] for r in c.fetchall()]
set_to_null.extend(empty_ids)

print(f'Relative→Full path fix: {len(fix_rel_to_full)}')
print(f'Set to NULL (truly broken): {len(remaining_rel)}')
print(f'Empty string → NULL: {len(empty_ids)}')
print(f'Total NULL: {len(remaining_rel) + len(empty_ids)}')

if fix_rel_to_full:
    c.executemany("UPDATE tracks SET lyrics_text_path = ? WHERE id = ?", 
                  [(p, i) for i, p in fix_rel_to_full])
    print(f'Fixed {len(fix_rel_to_full)} relative paths')

if set_to_null:
    for tid in set_to_null:
        c.execute("UPDATE tracks SET lyrics_text_path = NULL WHERE id = ?", (tid,))
    print(f'Set {len(set_to_null)} paths to NULL')

db.commit()

# Verify
c.execute("SELECT COUNT(*) FROM tracks WHERE lyrics_text_path IS NOT NULL AND lyrics_text_path != ''")
after = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM tracks WHERE lyrics_text_path IS NULL OR lyrics_text_path = ''")
missing_after = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM tracks WHERE lyrics_text_path IS NOT NULL AND lyrics_text_path != ''")
total_paths = c.fetchone()[0]

# Check bad paths after fix
bad = 0
c.execute("SELECT lyrics_text_path FROM tracks WHERE lyrics_text_path IS NOT NULL AND lyrics_text_path != ''")
for row in c.fetchall():
    if not os.path.exists(row[0]):
        bad += 1

print(f'\nAfter reconciliation:')
print(f'  有路径: {after}')
print(f'  缺失: {missing_after}')
print(f'  路径文件存在: {total_paths - bad}')
print(f'  路径文件不存在: {bad}')

db.close()
print('\nDone ✅')
