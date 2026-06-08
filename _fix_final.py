import sqlite3
conn = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
cur = conn.cursor()

# Fix 1: 海朋森 - album_id=446, 补2条 listen_history (2026)
for i in range(2):
    month = 1 + i
    cur.execute("INSERT INTO listen_history (album_id, listen_date, listen_year, notes, source) VALUES (?, ?, ?, ?, ?)",
        (446, f'2026-{month:02d}-15', 2026, '', ''))
print("Added 2 listen_history for 海朋森 id=446")

# Fix 2: 何寒寒 - 查看名字
cur.execute("SELECT album_id, album_name, artist FROM albums WHERE artist LIKE '%何寒%' OR artist LIKE '%κ寒%'")
r = cur.fetchall()
print(f"何寒寒 matches: {r}")

# 直接插入缺失专辑
cur.execute("SELECT album_id, album_name, artist, total_listen_count, first_listen_date, cover_image_url, country, region, genre, style, release_year, duration, release_company FROM albums_2026 WHERE album_id=195")
row = cur.fetchone()
if row:
    cols = [d[0] for d in cur.description]
    data = dict(zip(cols, row))
    cur.execute("""
        INSERT INTO albums (album_name, artist, total_listen_count, first_listen_date, 
            cover_image_url, country, region, genre, style, release_year, duration, release_company)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (data['album_name'], data['artist'], data.get('total_listen_count', 1),
        data.get('first_listen_date'), data.get('cover_image_url'), data.get('country'),
        data.get('region'), data.get('genre'), data.get('style'), data.get('release_year'),
        data.get('duration'), data.get('release_company')))
    new_id = cur.lastrowid
    print(f"Inserted 何寒寒 album id={new_id}")
    cur.execute("INSERT INTO listen_history (album_id, listen_date, listen_year, notes, source) VALUES (?, ?, ?, ?, ?)",
        (new_id, '2026-12-15', 2026, '', ''))

conn.commit()

# Verify
cur.execute("SELECT listen_year, COUNT(*) FROM listen_history GROUP BY listen_year ORDER BY listen_year")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]} records")

# Verify 2026 top
cur.execute("""
    SELECT a.album_name, a.artist, COUNT(lh.id) as cnt
    FROM listen_history lh JOIN albums a ON lh.album_id = a.album_id
    WHERE lh.listen_year = 2026
    GROUP BY lh.album_id ORDER BY cnt DESC LIMIT 10
""")
print("\n2026 Top 10:")
for r in cur.fetchall():
    print(f"  {r[0]} - {r[1]}: {r[2]}")

conn.close()
