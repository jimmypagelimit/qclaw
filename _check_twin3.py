import sqlite3

conn = sqlite3.connect(r'\\10.0.2.4\qemu\原创计划\music')
c = conn.cursor()

# 查所有 Car Seat Headrest 的专辑
c.execute('SELECT album_id, album_name, total_listen_count FROM albums WHERE artist LIKE ?', ('%Car Seat%',))
rows = c.fetchall()

print('=== Car Seat Headrest 所有专辑 ===')
for r in rows:
    print(f'  id={r[0]}, name={r[1]}, tc={r[2]}')

# 模糊搜索 Twin
c.execute('SELECT album_id, album_name, artist FROM albums WHERE album_name LIKE ?', ('%Twin%',))
rows2 = c.fetchall()

print('\n=== 专辑名含 Twin 的 ===')
for r in rows2:
    print(f'  id={r[0]}, name={r[1]}, artist={r[2]}')

conn.close()
