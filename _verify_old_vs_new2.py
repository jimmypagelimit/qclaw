import sqlite3
conn = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
cur = conn.cursor()

for tbl in ['albums_2024','albums_2025','albums_2026']:
    year = int(tbl.replace('albums_', ''))
    print(f"\n=== {tbl} vs listen_history ({year}) ===")
    cur.execute(f"SELECT album_name, artist, total_listen_count FROM {tbl}")
    old_rows = cur.fetchall()
    print(f"{tbl} 记录数: {len(old_rows)}")
    mismatch = 0
    missing = 0
    for alb_name, artist, old_cnt in old_rows:
        cur.execute("SELECT album_id FROM albums WHERE album_name=? AND artist=?", (alb_name, artist))
        r = cur.fetchone()
        if not r:
            print(f"  [缺失] 总表无此专辑: {alb_name} - {artist}")
            missing += 1
            continue
        album_id = r[0]
        cur.execute("SELECT COUNT(*) FROM listen_history WHERE album_id=? AND listen_year=?", (album_id, year))
        new_cnt = cur.fetchone()[0]
        if new_cnt != old_cnt:
            print(f"  [不符] {alb_name} - {artist}: 老表={old_cnt}, listen_history={new_cnt}")
            mismatch += 1
    if mismatch == 0 and missing == 0:
        print("  ✅ 完全一致，无遗漏")
    else:
        print(f"  共 {mismatch} 条不符, {missing} 条缺失")

print("\n核对完成。")
conn.close()
