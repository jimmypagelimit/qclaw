import sqlite3

conn = sqlite3.connect(r'\\10.0.2.4\qemu\原创计划\music')
c = conn.cursor()

# 查 albums 和 albums_2026 两张表
tables = ['albums', 'albums_2024', 'albums_2025', 'albums_2026']
for tbl in tables:
    c.execute(f'SELECT album_id, album_name, artist, total_listen_count FROM [{tbl}] WHERE album_name LIKE ?', ('%Twin%',))
    rows = c.fetchall()
    if rows:
        print(f'=== {tbl} ===')
        for r in rows:
            print(f'  id={r[0]}, name={r[1]}, artist={r[2]}, tc={r[3]}')

# 查 listen_history 是否有重复 album_id
c.execute('SELECT album_id, COUNT(*) as cnt FROM listen_history WHERE album_id=323 GROUP BY album_id')
print('\n=== listen_history album_id=323 ===')
for r in c.fetchall():
    print(f'  album_id={r[0]}, 记录数={r[1]}')

conn.close()
