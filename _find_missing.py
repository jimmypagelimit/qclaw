import sqlite3
conn = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
cur = conn.cursor()

year_tables = {
    'albums_2024': 2024,
    'albums_2025': 2025,
    'albums_2026': 2026,
}

# 手动映射：年度表中找不到的专辑 -> albums 表的正确记录
manual_mappings = {
    # 2026 id=33: 海朋森 [Hiperson] 的专辑名已改
    ('我不要你死于一事无成 No Need for Another History', '海朋森 [Hiperson]'): 446,
    # 模糊匹配
    ('Chinese Football', 'Chinese Football'): None,  # 需要查
    ('Det hjemsokte hjertet', 'Panopticon'): None,
    ('Wendy Eisenberg', 'Wendy Eisenberg'): None,
    ('Vol.II', 'Angine de Poitrine'): None,
    ('Teen of Denial (Joes Story)', 'Car Seat Headrest'): None,
}

# 查找模糊匹配
for name, artist in [k for k,v in manual_mappings.items() if v is None]:
    cur.execute("SELECT album_id, album_name, artist FROM albums WHERE artist LIKE ?", (f'%{artist}%',))
    results = cur.fetchall()
    for r in results:
        print(f"  Possible match: albums.id={r[0]}, '{r[1]}' by '{r[2]}'")

# 查 Chinese Football
cur.execute("SELECT album_id, album_name, artist FROM albums WHERE artist LIKE '%Chinese Football%'")
print("\nChinese Football matches:", cur.fetchall())

# 查 Panopticon
cur.execute("SELECT album_id, album_name, artist FROM albums WHERE artist LIKE '%Panopticon%'")
print("Panopticon matches:", cur.fetchall())

# 查 Wendy Eisenberg
cur.execute("SELECT album_id, album_name, artist FROM albums WHERE artist LIKE '%Wendy%'")
print("Wendy matches:", cur.fetchall())

# 查 Angine
cur.execute("SELECT album_id, album_name, artist FROM albums WHERE artist LIKE '%Angine%'")
print("Angine matches:", cur.fetchall())

# 查 Teen of Denial
cur.execute("SELECT album_id, album_name, artist FROM albums WHERE album_name LIKE '%Teen%Denial%'")
print("Teen of Denial matches:", cur.fetchall())

# 2024 not found
cur.execute("SELECT album_id, album_name, artist FROM albums WHERE artist LIKE '%陈%宇%' OR album_name LIKE '%风和日丽%'")
print("\n陈宇 matches:", cur.fetchall())

conn.close()
