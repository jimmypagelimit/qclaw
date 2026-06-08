import sqlite3

conn = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
cur = conn.cursor()

# 1. 修复 Teens of Denial - 删掉多出的 2 条 2026 年记录
print("=== 1. 修复 Teens of Denial ===")
cur.execute("SELECT album_id FROM albums WHERE album_name='Teens of Denial' AND artist='Car Seat Headrest'")
r = cur.fetchone()
if r:
    aid = r[0]
    cur.execute("SELECT id, listen_date FROM listen_history WHERE album_id=? AND listen_year=2026 ORDER BY id", (aid,))
    rows = cur.fetchall()
    print(f"  2026 年共 {len(rows)} 条: {[x[1] for x in rows]}")
    if len(rows) > 2:
        to_delete = [x[0] for x in rows[2:]]
        for did in to_delete:
            cur.execute("DELETE FROM listen_history WHERE id=?", (did,))
        print(f"  已删除 {len(to_delete)} 条 (id={to_delete})")
    # 更新 total_listen_count
    cur.execute("SELECT COUNT(*) FROM listen_history WHERE album_id=?", (aid,))
    new_total = cur.fetchone()[0]
    cur.execute("UPDATE albums SET total_listen_count=? WHERE album_id=?", (new_total, aid))
    print(f"  total_listen_count 更新为 {new_total}")
else:
    print("  未找到专辑")

# 2. 新增 Teen of Denial (Joes Story)
print("\n=== 2. 新增 Teen of Denial (Joes Story) ===")
cur.execute("SELECT album_id FROM albums WHERE album_name LIKE '%Joes Story%'")
r = cur.fetchone()
if r:
    new_aid = r[0]
    print(f"  已存在: album_id={new_aid}，跳过新增")
else:
    cur.execute("""
        INSERT INTO albums (album_name, artist, total_listen_count, release_year, country, region, genre, style)
        VALUES (?, ?, 2, 2016, '美国', '北美洲', 'Indie Rock', 'Rock')
    """, ('Teen of Denial (Joes Story)', 'Car Seat Headrest'))
    new_aid = cur.lastrowid
    print(f"  新增专辑: album_id={new_aid}")

# 3. 补入 Teen of Denial (Joes Story) 的 2 条 listen_history
print("\n=== 3. 补入 Teen of Denial (Joes Story) listen_history ===")
cur.execute("SELECT COUNT(*) FROM listen_history WHERE album_id=? AND listen_year=2026", (new_aid,))
cnt = cur.fetchone()[0]
if cnt == 0:
    cur.execute("INSERT INTO listen_history (album_id, listen_date, listen_year, source) VALUES (?, ?, ?, ?)",
                (new_aid, '2026-01-15', 2026, 'rebuild'))
    cur.execute("INSERT INTO listen_history (album_id, listen_date, listen_year, source) VALUES (?, ?, ?, ?)",
                (new_aid, '2026-02-15', 2026, 'rebuild'))
    print("  补入 2 条 2026 年记录（日期占位，需确认具体日期）")
    # 更新 total_listen_count
    cur.execute("UPDATE albums SET total_listen_count=2 WHERE album_id=?", (new_aid,))
else:
    print(f"  已有 {cnt} 条，跳过")

# 提交
conn.commit()

# 验证
print("\n=== 验证 ===")
cur.execute("SELECT COUNT(*) FROM listen_history WHERE album_id=? AND listen_year=2026", (aid,))
print(f"Teens of Denial 2026 年: {cur.fetchone()[0]} 条（目标: 2）")
cur.execute("SELECT COUNT(*) FROM listen_history WHERE album_id=? AND listen_year=2026", (new_aid,))
print(f"Teen of Denial (Joes Story) 2026 年: {cur.fetchone()[0]} 条（目标: 2）")

conn.close()
print("\n完成。")
