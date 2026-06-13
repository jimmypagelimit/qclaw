import os, glob

# Correct database path
CORRECT_DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'

# Find all _music*.db files
workspace = r'C:\Users\qujt\.qclaw\workspace'
db_files = glob.glob(os.path.join(workspace, '_music*.db'))
db_files += glob.glob(os.path.join(workspace, '**', '_music*.db'), recursive=True)

print(f'Found {len(db_files)} database files:')
to_delete = []
for f in db_files:
    if os.path.abspath(f) != os.path.abspath(CORRECT_DB):
        size_mb = os.path.getsize(f) / (1024*1024)
        to_delete.append(f)
        print(f'  DELETE: {f} ({size_mb:.1f} MB)')
    else:
        size_mb = os.path.getsize(f) / (1024*1024)
        print(f'  KEEP: {f} ({size_mb:.1f} MB)')

print(f'\nDeleting {len(to_delete)} files...')
deleted = 0
for f in to_delete:
    try:
        os.remove(f)
        print(f'  Deleted: {f}')
        deleted += 1
    except Exception as e:
        print(f'  ERROR deleting {f}: {e}')

print(f'\nDone! Deleted {deleted} files')
print(f'Remaining: {CORRECT_DB}')
