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

if missing > 0:
    print("=== 缺失 MBID 的专辑（前20张）===")
    c.execute("SELECT album_id, album_name, artist FROM albums WHERE release_mbid IS NULL OR release_mbid = '' ORDER BY artist LIMIT 20")
    for r in c.fetchall():
        print(f"  id={r[0]} | {r[2]} - {r[1]}")

conn.close()
