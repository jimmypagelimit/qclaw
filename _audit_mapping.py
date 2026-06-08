import sqlite3
conn = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
cur = conn.cursor()

# 统计：listen_history 中 2026 年有多少条记录的 album_id 需要修正
# 方法：对比 albums_2026 的 (album_name, artist) -> albums 表的正确 album_id

# 先获取所有年度表
year_tables = ['albums_2024', 'albums_2025', 'albums_2026']

total_wrong = 0
total_correct = 0

for yt in year_tables:
    year = int(yt.replace('albums_', ''))
    
    # 获取年度表所有专辑
    cur.execute(f"SELECT album_id, album_name, artist FROM {yt}")
    year_albums = cur.fetchall()
    
    wrong = 0
    correct = 0
    
    for yid, yname, yartist in year_albums:
        # 在 albums 表找到正确的 album_id
        cur.execute("SELECT album_id FROM albums WHERE album_name=? AND artist=?", (yname, yartist))
        r = cur.fetchone()
        
        if r is None:
            # 专辑在 albums 表中找不到
            wrong += 1
            print(f"  {yt} id={yid}: '{yname}' by '{yartist}' NOT FOUND in albums")
        elif r[0] != yid:
            # ID 不匹配
            wrong += 1
            # 只打印前10条
            if wrong <= 10:
                print(f"  {yt} id={yid} -> albums id={r[0]}: '{yname}' by '{yartist}'")
        else:
            correct += 1
    
    total_wrong += wrong
    total_correct += correct
    print(f"\n{yt}: {correct} correct, {wrong} wrong\n")

print(f"TOTAL: {total_correct} correct, {total_wrong} wrong")

conn.close()
