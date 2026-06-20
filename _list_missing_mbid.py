import sqlite3

db = 'C:/Users/qujt/.qclaw/workspace/_music_latest.db'
conn = sqlite3.connect(db)
c = conn.cursor()

c.execute("SELECT COUNT(*) FROM albums")
total = c.fetchone()[0]

c.execute("SELECT COUNT(*) FROM albums WHERE release_mbid IS NOT NULL AND release_mbid != ''")
has_mbid = c.fetchone()[0]

c.execute("SELECT COUNT(*) FROM albums WHERE release_mbid IS NULL OR release_mbid = ''")
missing = c.fetchone()[0]

print(f"专辑总数: {total}")
print(f"已有 MBID: {has_mbid} ({has_mbid/total*100:.1f}%)")
print(f"MBID 缺失: {missing}")
print()
print("=" * 60)
print("缺失 MBID 的专辑列表（按艺人排序）")
print("=" * 60)

c.execute("SELECT album_id, album_name, artist FROM albums WHERE release_mbid IS NULL OR release_mbid = '' ORDER BY artist, album_name")
rows = c.fetchall()

with open('C:/Users/qujt/.qclaw/workspace/_mbid_missing_list.txt', 'w', encoding='utf-8') as f:
    f.write(f"专辑总数: {total}\n")
    f.write(f"已有 MBID: {has_mbid} ({has_mbid/total*100:.1f}%)\n")
    f.write(f"MBID 缺失: {missing}\n\n")
    f.write("=" * 60 + "\n")
    f.write("缺失 MBID 的专辑列表（按艺人排序）\n")
    f.write("=" * 60 + "\n\n")
    
    for r in rows:
        line = f"  id={r[0]} | {r[2]} - {r[1]}"
        print(line)
        f.write(line + "\n")

print(f"\n完整列表已保存到: _mbid_missing_list.txt")
conn.close()
