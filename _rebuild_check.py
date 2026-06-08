import sqlite3
conn = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
cur = conn.cursor()

# 重建 listen_history 的策略：
# 1. 清空 listen_history
# 2. 从年度表重建：对每个年度表的每条记录，在 albums 表找到正确 album_id
# 3. 生成对应数量的 listen_history 记录
# 4. 对于 NOT FOUND 的专辑，先在 albums 表中插入

year_tables = {
    'albums_2024': 2024,
    'albums_2025': 2025,
    'albums_2026': 2026,
}

not_found = []
inserted = 0
matched = 0

for yt, year in year_tables.items():
    cur.execute(f"SELECT album_id, album_name, artist, total_listen_count, first_listen_date FROM {yt}")
    rows = cur.fetchall()
    
    for yid, name, artist, tlc, fld in rows:
        # 在 albums 表找正确的 album_id
        cur.execute("SELECT album_id FROM albums WHERE album_name=? AND artist=?", (name, artist))
        r = cur.fetchone()
        
        if r is None:
            not_found.append((year, yid, name, artist))
            continue
        
        album_id = r[0]
        matched += 1

print(f"Matched: {matched}")
print(f"Not found: {len(not_found)}")
for year, yid, name, artist in not_found:
    print(f"  {year} id={yid}: {name} - {artist}")

conn.close()
