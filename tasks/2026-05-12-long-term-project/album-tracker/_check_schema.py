import sqlite3, os

db = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\_music_latest.db'
print('DB exists:', os.path.exists(db))
conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
print('=== Tables ===')
for t in cur.fetchall():
    print(' ', t[0])

print('\n=== artists columns ===')
try:
    cur.execute('PRAGMA table_info(artists)')
    for r in cur.fetchall():
        print(r)
except Exception as e:
    print(f'  Error: {e}')

print('\n=== Sample artists ===')
try:
    cur.execute('SELECT * FROM artists LIMIT 5')
    cols = [d[0] for d in cur.description]
    print('Columns:', cols)
    for r in cur.fetchall():
        print(r)
except Exception as e:
    print(f'  Error: {e}')
conn.close()
