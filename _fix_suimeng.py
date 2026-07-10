import sqlite3

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()

album_id = 599

# 查看当前所有记录
cur.execute('SELECT id, listen_date FROM listen_history WHERE album_id=? ORDER BY listen_date', (album_id,))
records = cur.fetchall()
print(f'当前 {len(records)} 条记录:')
for r in records:
    print(f'  ID={r[0]}, date={r[1]}')

# 删除多余的11条（保留最早的2条）
if len(records) > 2:
    # 按日期排序，保留前2条
    keep_ids = [r[0] for r in records[:2]]
    delete_ids = [r[0] for r in records[2:]]
    
    print(f'\n保留 ID: {keep_ids}')
    print(f'删除 ID: {delete_ids}')
    
    for did in delete_ids:
        cur.execute('DELETE FROM listen_history WHERE id=?', (did,))
    
    conn.commit()
    print(f'已删除 {len(delete_ids)} 条记录')

# 验证
cur.execute('SELECT COUNT(*) FROM listen_history WHERE album_id=?', (album_id,))
final_count = cur.fetchone()[0]
print(f'\n最终听歌次数: {final_count}')

conn.close()
