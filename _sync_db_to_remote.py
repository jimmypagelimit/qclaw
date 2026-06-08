import sqlite3, os

# Load from the latest database.sql
sql_path = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\database.sql'
db_path = r'C:\Users\qujt\.qclaw\_music_sync.db'

if os.path.exists(db_path):
    os.remove(db_path)

conn = sqlite3.connect(db_path)
with open(sql_path, 'r', encoding='utf-8') as f:
    conn.executescript(f.read())

# Verify the new DB has the intermediate tables
cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in cur.fetchall()]
print('Tables in SQL-derived DB:', tables)

for t in ['album_genres', 'album_styles']:
    if t in tables:
        cur2 = conn.execute('SELECT COUNT(*) FROM [%s]' % t)
        print('  %s: %d rows' % (t, cur2.fetchone()[0]))

# Compare with remote
cur3 = conn.execute('SELECT COUNT(*) FROM albums')
albums = cur3.fetchone()[0]
cur4 = conn.execute('SELECT COUNT(*) FROM listen_history')
lh = cur4.fetchone()[0]
print('albums: %d, listen_history: %d' % (albums, lh))

conn.close()

# Now copy to remote
import shutil
remote_path = r'\\10.0.2.4\qemu\原创计划\music'
print('\nCopying %s -> %s ...' % (db_path, remote_path))
print('Remote current size:', os.path.getsize(remote_path))

# Backup remote first
backup_path = r'\\10.0.2.4\qemu\原创计划\music_backup_20260608'
if not os.path.exists(backup_path):
    shutil.copy2(remote_path, backup_path)
    print('Backup created: %s (%d bytes)' % (backup_path, os.path.getsize(backup_path)))
else:
    print('Backup already exists')

# Copy new DB to remote
shutil.copy2(db_path, remote_path)
print('Copied! Remote new size:', os.path.getsize(remote_path))

# Verify
conn2 = sqlite3.connect(remote_path)
cur5 = conn2.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables2 = [r[0] for r in cur5.fetchall()]
print('Remote tables after copy:', tables2)
cur6 = conn2.execute('SELECT COUNT(*) FROM albums')
print('Remote albums:', cur6.fetchone()[0])
for t in ['album_genres', 'album_styles']:
    if t in tables2:
        cur7 = conn2.execute('SELECT COUNT(*) FROM [%s]' % t)
        print('  %s: %d rows' % (t, cur7.fetchone()[0]))
conn2.close()

# Cleanup
os.remove(db_path)
print('\nDone! Database synced to remote.')
