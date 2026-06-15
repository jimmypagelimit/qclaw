import sqlite3
db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

# albums 表结构
cur.execute('PRAGMA table_info(albums)')
cols = cur.fetchall()
print('=== albums 表字段 ===')
for c in cols:
    print(f'  {c[1]} ({c[2]})')

# 字段完整度
print()
print('=== albums 字段完整度 ===')
cur.execute('SELECT COUNT(*) FROM albums')
total = cur.fetchall()[0][0]
cur.execute('PRAGMA table_info(albums)')
for c in cur.fetchall():
    col = c[1]
    cur.execute(f'SELECT COUNT(*) FROM albums WHERE {col} IS NOT NULL AND {col} != ""')
    filled = cur.fetchone()[0]
    pct = 100*filled//total if total > 0 else 0
    print(f'  {col}: {filled}/{total} ({pct}%)')

# artists 表结构
print()
cur.execute('PRAGMA table_info(artists)')
cols = cur.fetchall()
print('=== artists 表字段 ===')
for c in cols:
    print(f'  {c[1]} ({c[2]})')

print()
print('=== artists 字段完整度 ===')
cur.execute('SELECT COUNT(*) FROM artists')
total = cur.fetchone()[0]
cur.execute('PRAGMA table_info(artists)')
for c in cur.fetchall():
    col = c[1]
    cur.execute(f'SELECT COUNT(*) FROM artists WHERE {col} IS NOT NULL AND {col} != ""')
    filled = cur.fetchone()[0]
    pct = 100*filled//total if total > 0 else 0
    print(f'  {col}: {filled}/{total} ({pct}%)')

conn.close()
