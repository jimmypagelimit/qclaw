import sqlite3, collections

DB_UNC = r'\\10.0.2.4\qemu\原创计划\music'
conn = sqlite3.connect(DB_UNC)
c = conn.cursor()

# 按 album_name + artist 分组，找出现次数>1的
c.execute('SELECT album_name, artist, COUNT(*) as cnt FROM albums GROUP BY album_name, artist HAVING cnt > 1')
dupes = c.fetchall()

print(f'=== 重复专辑（tc>0） ===')
print(f'共 {len(dupes)} 组重复\n')

total_extra = 0
for name, artist, cnt in dupes:
    c.execute('SELECT album_id, album_name, artist, total_listen_count FROM albums WHERE album_name = ? AND artist = ? ORDER BY total_listen_count DESC', (name, artist))
    rows = c.fetchall()
    print(f'{artist} - {name} ({cnt} 条):')
    for r in rows:
        print(f'  id={r[0]}, tc={r[3]}')
    total_extra += (cnt - 1)

print(f'\n共 {total_extra} 条多余记录需合并')
conn.close()
