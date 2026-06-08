import sqlite3

conn = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
cur = conn.cursor()

print("=== 1. Teens of Denial - Car Seat Headrest ===")
cur.execute("SELECT album_id, total_listen_count FROM albums WHERE album_name='Teens of Denial' AND artist='Car Seat Headrest'")
r = cur.fetchone()
if r:
    aid = r[0]
    print(f"album_id={aid}, total={r[1]}")
    cur.execute("SELECT id, listen_year, listen_month, listen_day FROM listen_history WHERE album_id=? ORDER BY id", (aid,))
    rows = cur.fetchall()
    print(f"listen_history 共 {len(rows)} 条:")
    for row in rows:
        print(f"  id={row[0]}, {row[1]}-{row[2]:02d}-{row[3]:02d}")
else:
    print("未找到")

print("\n=== 2. Teen of Denial (Joes Story) - Car Seat Headrest ===")
cur.execute("SELECT album_id FROM albums WHERE album_name LIKE '%Teen of Denial%' OR album_name LIKE '%Joes Story%'")
r = cur.fetchone()
print(f"总表: {'album_id='+str(r[0]) if r else '未找到，需新增'}")

print("\n=== 3. 我不要别的历史 - 海朋森 ===")
cur.execute("SELECT album_id, total_listen_count FROM albums WHERE album_name LIKE '%不要别的历史%'")
r = cur.fetchone()
if r:
    aid = r[0]
    print(f"album_id={aid}, total={r[1]}")
    cur.execute("SELECT COUNT(*) FROM listen_history WHERE album_id=? AND listen_year=2026", (aid,))
    print(f"2026 listen_history: {cur.fetchone()[0]} 条")
else:
    print("未找到")

print("\n=== 4. 春子 Haruko - L8ching ===")
cur.execute("SELECT album_id, total_listen_count FROM albums WHERE album_name LIKE '%Haruko%'")
r = cur.fetchone()
if r:
    aid = r[0]
    print(f"album_id={aid}, total={r[1]}")
    cur.execute("SELECT COUNT(*) FROM listen_history WHERE album_id=? AND listen_year=2026", (aid,))
    print(f"2026 listen_history: {cur.fetchone()[0]} 条")

print("\n=== 5. Remains - 東京酒吐座 ===")
cur.execute("SELECT album_id, total_listen_count FROM albums WHERE album_name='Remains' AND artist='東京酒吐座'")
r = cur.fetchone()
if r:
    aid = r[0]
    print(f"album_id={aid}, total={r[1]}")
    cur.execute("SELECT COUNT(*) FROM listen_history WHERE album_id=? AND listen_year=2026", (aid,))
    print(f"2026 listen_history: {cur.fetchone()[0]} 条")

conn.close()
