import sqlite3

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'

conn = sqlite3.connect(DB)
cur = conn.cursor()

# 先查看
cur.execute("SELECT id, album_id, listen_date FROM listen_history WHERE album_id=555 ORDER BY id")
records = cur.fetchall()

print("Current listen records for Olivia Rodrigo:")
for r in records:
    print(f"  id={r[0]} album_id={r[1]} date={r[2]}")

# 保留第1、2、3条，删除最后一条（第4条）
if len(records) > 3:
    to_delete = records[-1]  # 最后一条
    print(f"\nFound {len(records)} records, expected 3.")
    print(f"Deleting extra record: id={to_delete[0]} date={to_delete[2]}")
    
    cur.execute("DELETE FROM listen_history WHERE id=?", (to_delete[0],))
    conn.commit()
    
    # 核实
    cur.execute("SELECT COUNT(*) FROM listen_history WHERE album_id=555")
    final = cur.fetchone()[0]
    print(f"Done. Deleted id={to_delete[0]}. Now {final} records.")
else:
    print(f"\n{len(records)} records. No extra record to delete.")

conn.close()
