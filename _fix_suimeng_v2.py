import sqlite3

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()

# 碎梦飞跃《外面是夏天》(ID=599)
album_id = 599

# 查看当前所有记录
cur.execute('SELECT id, listen_date FROM listen_history WHERE album_id=? ORDER BY listen_date', (album_id,))
records = cur.fetchall()
print(f'当前 {len(records)} 条记录:')
for r in records:
    print(f'  ID={r[0]}, date={r[1]}')

# 只保留1条（最早的那个）
if len(records) > 1:
    # 删除除了第一条之外的所有记录
    keep_id = records[0][0]
    for r in records[1:]:
        cur.execute('DELETE FROM listen_history WHERE id=?', (r[0],))
        print(f'  删除 ID={r[0]}')
    
    conn.commit()
    print(f'\n已删除 {len(records)-1} 条记录，保留 ID={keep_id}')

# 验证
cur.execute('SELECT COUNT(*) FROM listen_history WHERE album_id=?', (album_id,))
final_count = cur.fetchone()[0]
print(f'\n最终听歌次数: {final_count}')

conn.close()
