import sqlite3
conn = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
cur = conn.cursor()

results = []
for tbl in ['albums_2024','albums_2025','albums_2026']:
    year = int(tbl.replace('albums_', ''))
    cur.execute(f"SELECT album_name, artist, total_listen_count FROM {tbl}")
    old_rows = cur.fetchall()
    mismatches = []
    missing = []
    for alb_name, artist, old_cnt in old_rows:
        cur.execute("SELECT album_id FROM albums WHERE album_name=? AND artist=?", (alb_name, artist))
        r = cur.fetchone()
        if not r:
            missing.append(f"  缺失: 总表无此专辑: {alb_name} - {artist}")
            continue
        album_id = r[0]
        cur.execute("SELECT COUNT(*) FROM listen_history WHERE album_id=? AND listen_year=?", (album_id, year))
        new_cnt = cur.fetchone()[0]
        if new_cnt != old_cnt:
            mismatches.append(f"  不符: {alb_name} - {artist}: 老表={old_cnt}, listen_history={new_cnt}")
    status = f"{tbl}: {len(old_rows)}条, {len(mismatches)}条不符, {len(missing)}条缺失"
    results.append(status)
    results.append(f"\n=== {tbl} vs listen_history ({year}) ===")
    results.append(f"  共 {len(old_rows)} 条记录")
    results.extend(mismatches)
    results.extend(missing)
    if not mismatches and not missing:
        results.append("  [OK] 完全一致，无遗漏")

results.append("\n核对完成。")
output = '\n'.join(results)
print(output)

with open(r'C:\Users\qujt\.qclaw\workspace\_verify_result.txt', 'w', encoding='utf-8') as f:
    f.write(output)

conn.close()
