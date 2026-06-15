import sqlite3

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
c = conn.cursor()

# Check external_* tables
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'external_%'")
tables = c.fetchall()
print(f'Satellite tables: {len(tables)}')
for t in tables:
    c.execute(f'SELECT COUNT(*) FROM {t[0]}')
    cnt = c.fetchone()[0]
    print(f'  {t[0]}: {cnt} rows')

# Check views
c.execute("SELECT name FROM sqlite_master WHERE type='view'")
views = c.fetchall()
print(f'\nViews: {len(views)}')
for v in views:
    print(f'  {v[0]}')

# Check external_ratings coverage by source
c.execute('SELECT source, COUNT(*) FROM external_ratings GROUP BY source')
rows = c.fetchall()
if rows:
    print(f'\nexternal_ratings by source:')
    for r in rows:
        print(f'  {r[0]}: {r[1]} rows')
else:
    print('\nexternal_ratings: empty or not exists')

conn.close()
