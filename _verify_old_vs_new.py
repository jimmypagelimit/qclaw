import sqlite3
conn = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
cur = conn.cursor()

# 检查年度表是否还存在
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'albums_20%'")
old_tables = [r[0] for r in cur.fetchall()]
print('年度表:', old_tables if old_tables else '已删除')

# 如果有，开始核对
for tbl in old_tables:
    year = tbl.replace('albums_', '')
    print(f"\n=== {tbl} vs listen_history ({year}) ===")
    cur.execute(f"SELECT album_name, artist, listen_count FROM {tbl}")
    old_rows = cur.fetchall()
    print(f"{tbl} 记录数: {len(old_rows)}")
    for alb_name, artist, old_cnt in old_rows:
        # 在 albums 总表找 album_id
        cur.execute("SELECT album_id FROM albums WHERE album_name=? AND artist=?", (alb_name, artist))
        r = cur.fetchone()
        if not r:
            print(f"  [WARN] 总表缺失: {alb_name} - {artist}")
            continue
        album_id = r[0]
        cur.execute("SELECT COUNT(*) FROM listen_history WHERE album_id=? AND listen_year=?", (album_id, int(year)))
        new_cnt = cur.fetchone()[0]
        if new_cnt != old_cnt:
            print(f"  [DIFF] {alb_name} - {artist}: 老表={old_cnt}, 新表={new_cnt}")

print("\n核对完成。")
conn.close()
