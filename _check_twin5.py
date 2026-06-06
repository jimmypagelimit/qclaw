import sqlite3
import json

conn = sqlite3.connect(r'\\10.0.2.4\qemu\原创计划\music')
conn.row_factory = sqlite3.Row
c = conn.cursor()

# 1. 查 albums 表
c.execute('SELECT * FROM albums WHERE album_id = 323')
row = c.fetchone()
print('=== albums 表 id=323 ===')
if row:
    cols = [desc[0] for desc in c.description]
    for col, val in zip(cols, row):
        print(f'  {col}: {val}')

# 2. 查 albums_2025 和 albums_2026
for tbl in ['albums_2024', 'albums_2025', 'albums_2026']:
    c.execute(f'SELECT * FROM [{tbl}] WHERE album_name LIKE ?', ('%Twin%',))
    rows = c.fetchall()
    if rows:
        print(f'\n=== {tbl} ===')
        for r in rows:
            cols = [desc[0] for desc in c.description]
            for col, val in zip(cols, r):
                print(f'  {col}: {val}')

# 3. 查 listen_history
c.execute('SELECT listen_date, listen_year FROM listen_history WHERE album_id = 323 ORDER BY listen_date')
rows = c.fetchall()
print(f'\n=== listen_history album_id=323 ({len(rows)} 条) ===')
for r in rows:
    print(f'  {r[0]} (year={r[1]})')

# 4. 按年统计
c.execute('SELECT listen_year, COUNT(*) as cnt FROM listen_history WHERE album_id = 323 GROUP BY listen_year')
print('\n=== 按年统计 ===')
for r in c.fetchall():
    print(f'  {r[0]}: {r[1]} 次')

conn.close()
