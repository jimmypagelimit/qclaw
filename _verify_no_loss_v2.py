import sqlite3

DB_UNC = r'\\10.0.2.4\qemu\原创计划\music'

print('=== 专辑丢失验证 ===\n')
conn = sqlite3.connect(DB_UNC)
c = conn.cursor()

# 1. 外键完整性检查
print('[1/4] listen_history → albums 外键完整性...')
c.execute('SELECT DISTINCT album_id FROM listen_history ORDER BY album_id')
history_ids = [r[0] for r in c.fetchall()]

c.execute('SELECT album_id FROM albums')
album_ids = set(r[0] for r in c.fetchall())

missing = [id_ for id_ in history_ids if id_ not in album_ids]
if missing:
    print(f'  ❌ 丢失: listen_history 中有 {len(missing)} 个 album_id 在 albums 表中不存在')
    print(f'  IDs: {missing[:20]}...')
else:
    print(f'  ✅ 完整: listen_history 中 {len(history_ids)} 个不同 album_id 全部存在于 albums 表')

# 2. 统计：当前 albums 表数量
print('\n[2/4] 统计当前数据...')
c.execute('SELECT COUNT(*) FROM albums')
albums_cnt = c.fetchone()[0]
c.execute('SELECT COUNT(*) FROM listen_history')
history_cnt = c.fetchone()[0]
c.execute('SELECT COUNT(DISTINCT album_id) FROM listen_history')
distinct_cnt = c.fetchone()[0]
print(f'  albums 表: {albums_cnt} 条')
print(f'  listen_history 表: {history_cnt} 条')
print(f'  listen_history 不同 album_id: {distinct_cnt} 个')

# 3. 检查 albums 表中是否有 album_name+artist 为 NULL 或空
print('\n[3/4] 检查空字段...')
c.execute('SELECT COUNT(*) FROM albums WHERE album_name IS NULL OR album_name = ""')
null_name = c.fetchone()[0]
c.execute('SELECT COUNT(*) FROM albums WHERE artist IS NULL OR artist = ""')
null_artist = c.fetchone()[0]
if null_name or null_artist:
    print(f'  ⚠️ album_name 为空: {null_name} 条')
    print(f'  ⚠️ artist 为空: {null_artist} 条')
else:
    print(f'  ✅ 无空字段')

# 4. 验证：随机抽查几个 listen_history 的 album_id 是否能正确 JOIN
print('\n[4/4] 随机抽查 JOIN...')
c.execute('SELECT album_id FROM listen_history LIMIT 5')
sample_ids = [r[0] for r in c.fetchall()]
for aid in sample_ids:
    c.execute('SELECT album_name, artist FROM albums WHERE album_id = ?', (aid,))
    row = c.fetchone()
    if row:
        print(f'  album_id={aid}: {row[1]} - {row[0]}')
    else:
        print(f'  ❌ album_id={aid}: 在 albums 表中找不到！')

conn.close()

print('\n=== 验证完成 ===')
if not missing:
    print('✅ 结论: 没有丢失专辑（所有 listen_history 中的 album_id 都能在 albums 表中找到）')
else:
    print(f'❌ 结论: 丢失了 {len(missing)} 个 album_id 对应的专辑')
