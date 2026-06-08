import sqlite3, os, shutil

# 备份
src = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
bak = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db.bak.before_rebuild'
shutil.copy2(src, bak)
print(f"Backed up to {bak}")

conn = sqlite3.connect(src)
cur = conn.cursor()

year_tables = {
    'albums_2024': 2024,
    'albums_2025': 2025,
    'albums_2026': 2026,
}

# 手动映射：年度表(album_name, artist) -> albums.album_id
manual_map = {
    # 海朋森 [Hiperson] 的专辑名在 albums 表已改为"我不要别的历史"
    ('我不要你死于一事无成 No Need for Another History', '海朋森 [Hiperson]'): 446,
    # Teen of Denial (Joes Story) -> Teens of Denial (拼写差异)
    ('Teen of Denial (Joes Story)', 'Car Seat Headrest'): 382,
}

# 这些在 albums 表中完全不存在，需要新增
# Chinese Football, Panopticon, Wendy Eisenberg, Angine de Poitrine, 风和日丽-陈宇
missing_albums = [
    # (album_name, artist, total_listen_count, year_table, year_id)
    ('Chinese Football', 'Chinese Football', 1, 'albums_2026', 123),
    ('Det hjemsokte hjertet', 'Panopticon', 1, 'albums_2026', 191),
    ('Wendy Eisenberg', 'Wendy Eisenberg', 1, 'albums_2026', 192),
    ('Vol.II', 'Angine de Poitrine', 1, 'albums_2026', 193),
    ('风和日丽', '陈宇', 1, 'albums_2024', 207),
]

# 插入缺失专辑到 albums 表
for name, artist, tlc, yt, yid in missing_albums:
    # 先检查是否已存在
    cur.execute("SELECT album_id FROM albums WHERE album_name=? AND artist=?", (name, artist))
    if cur.fetchone():
        continue
    # 从年度表获取更多信息
    cur.execute(f"SELECT * FROM {yt} WHERE album_id=?", (yid,))
    row = cur.fetchone()
    if row:
        cols = [d[0] for d in cur.description]
        data = dict(zip(cols, row))
        cur.execute("""
            INSERT INTO albums (album_name, artist, country, region, genre, rating,
                description, is_compilation, first_listen_date, total_listen_count,
                release_company, cover_image_url, duration, release_year, style, producer)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.get('album_name'), data.get('artist'), data.get('country'), 
            data.get('region'), data.get('genre'), data.get('rating'),
            data.get('description'), data.get('is_compilation', 0), 
            data.get('first_listen_date'), data.get('total_listen_count', 1),
            data.get('release_company'), data.get('cover_image_url'), 
            data.get('duration'), data.get('release_year'), data.get('style'), data.get('producer')
        ))
        print(f"Inserted: {name} - {artist} (id will be assigned)")

conn.commit()

# 现在重建 listen_history
# 1. 清空
cur.execute("DELETE FROM listen_history")
print(f"Cleared listen_history")

# 2. 从年度表重建
total_records = 0
skipped = 0

for yt, year in year_tables.items():
    cur.execute(f"SELECT album_id, album_name, artist, total_listen_count, first_listen_date FROM {yt}")
    rows = cur.fetchall()
    
    for yid, name, artist, tlc, fld in rows:
        tlc = tlc or 1
        
        # 找正确的 albums.album_id
        album_id = None
        
        # 先查手动映射
        if (name, artist) in manual_map:
            album_id = manual_map[(name, artist)]
        else:
            cur.execute("SELECT album_id FROM albums WHERE album_name=? AND artist=?", (name, artist))
            r = cur.fetchone()
            if r:
                album_id = r[0]
        
        if album_id is None:
            skipped += 1
            print(f"  SKIP: {year} '{name}' by '{artist}' - not found in albums")
            continue
        
        # 生成 listen_history 记录
        # 分散到全年各月
        listen_date = fld or f'{year}-01-15'
        base_month = int(listen_date[5:7]) if listen_date and len(listen_date) >= 7 else 1
        
        for i in range(tlc):
            # 简单分配日期：每月一条
            month = ((base_month - 1 + i) % 12) + 1
            date = f'{year}-{month:02d}-15'
            cur.execute(
                "INSERT INTO listen_history (album_id, listen_date, listen_year, notes, source) VALUES (?, ?, ?, ?, ?)",
                (album_id, date, year, '', '')
            )
            total_records += 1

conn.commit()
print(f"\nRebuilt listen_history: {total_records} records, {skipped} skipped")

# 验证
cur.execute("SELECT listen_year, COUNT(*) FROM listen_history GROUP BY listen_year ORDER BY listen_year")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]} records")

# 验证 2026 top 5
cur.execute("""
    SELECT a.album_name, a.artist, COUNT(lh.id) as cnt
    FROM listen_history lh
    JOIN albums a ON lh.album_id = a.album_id
    WHERE lh.listen_year = 2026
    GROUP BY lh.album_id
    ORDER BY cnt DESC
    LIMIT 5
""")
print("\n2026 Top 5 (new):")
for r in cur.fetchall():
    print(f"  {r[0]} - {r[1]}: {r[2]}")

conn.close()
