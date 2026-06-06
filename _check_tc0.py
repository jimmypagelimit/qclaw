import sqlite3

conn = sqlite3.connect(r'\\10.0.2.4\qemu\原创计划\music')
c = conn.cursor()

# 查所有 tc=0 的专辑
c.execute('SELECT album_id, album_name, artist, total_listen_count FROM albums WHERE total_listen_count = 0')
rows = c.fetchall()

print(f'=== total_listen_count = 0 的专辑（共 {len(rows)} 条）===' )
for r in rows:
    print(f'  id={r[0]}, name={r[1]}, artist={r[2]}, tc={r[3]}')

# 查 listen_history 是否有这些 album_id
print('\n=== listen_history 检查 ===')
for r in rows:
    c.execute('SELECT COUNT(*) FROM listen_history WHERE album_id = ?', (r[0],))
    cnt = c.fetchone()[0]
    if cnt > 0:
        print(f'  ⚠️  id={r[0]} 在 listen_history 中有 {cnt} 条记录！')

# 特别查 Car Seat Headrest 的
print('\n=== Car Seat Headrest 所有专辑 ===')
c.execute('SELECT album_id, album_name, total_listen_count FROM albums WHERE artist LIKE ?', ('%Car Seat%',))
for r in c.fetchall():
    print(f'  id={r[0]}, name={r[1]}, tc={r[2]}')

conn.close()
