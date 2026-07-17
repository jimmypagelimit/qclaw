import sqlite3

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
cur = conn.cursor()
# 删掉 id=2886（入库时自动生成的那条）
cur.execute("DELETE FROM listen_history WHERE id=2886")
conn.commit()
print(f'Rows deleted: {cur.rowcount}')

# 验证
cur.execute("SELECT COUNT(*) FROM listen_history WHERE album_id=611")
print(f'Remaining listens: {cur.fetchone()[0]}')
conn.close()
