import sqlite3

conn = sqlite3.connect(r'\\10.0.2.4\qemu\原创计划\music')
c = conn.cursor()

# 查 Twin Fantasy
c.execute('SELECT album_id, album_name, artist, total_listen_count FROM albums WHERE album_name LIKE ?', ('%Twin%',))
rows = c.fetchall()

print('=== Twin Fantasy 查询结果 ===')
for r in rows:
    print(f'  album_id={r[0]}, name={r[1]}, artist={r[2]}, tc={r[3]}')

# 也查 listen_history 数量
print('\n=== listen_history 分布 ===')
for r in rows:
    c.execute('SELECT COUNT(*) FROM listen_history WHERE album_id=?', (r[0],))
    cnt = c.fetchone()[0]
    print(f'  album_id={r[0]}: listen_history 有 {cnt} 条')

conn.close()
