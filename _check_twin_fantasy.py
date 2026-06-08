import sqlite3
conn = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
cur = conn.cursor()

# 查 Twin Fantasy 在 albums 表的信息
cur.execute("SELECT album_id, album_name, artist, total_listen_count FROM albums WHERE album_name LIKE '%Twin Fantasy%'")
albums = cur.fetchall()
for a in albums:
    print(f"album_id={a[0]}: {a[1]} - {a[2]} (total={a[3]})")

print()
for a in albums:
    # 查 listen_history 里 2026 年的记录
    cur.execute("SELECT id, listen_date, listen_year FROM listen_history WHERE album_id=? ORDER BY listen_date DESC", (a[0],))
    lh = cur.fetchall()
    print(f"  listen_history ({len(lh)} records):")
    for r in lh:
        print(f"    id={r[0]}, {r[1]}, year={r[2]}")
    y2026 = [r for r in lh if r[2] == 2026]
    print(f"  -> 2026年: {len(y2026)}次")

conn.close()
