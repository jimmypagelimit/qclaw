import sqlite3

db = 'C:/Users/qujt/.qclaw/workspace/_music_latest.db'
conn = sqlite3.connect(db)
c = conn.cursor()

c.execute("""SELECT album_id, album_name, artist 
    FROM albums 
    WHERE release_mbid IS NULL OR release_mbid = ''
    ORDER BY artist, album_name
""")
rows = c.fetchall()

with open('C:/Users/qujt/.qclaw/workspace/_mbid_remaining.txt', 'w', encoding='utf-8') as f:
    f.write(f"剩余缺失 MBID 的专辑：{len(rows)} 张\n")
    f.write("=" * 70 + "\n\n")
    
    for r in rows:
        # 生成 MusicBrainz 搜索链接
        import urllib.parse
        query = f"{r[2]} {r[1]}"
        url = f"https://musicbrainz.org/search/release-group?query={urllib.parse.quote(query)}"
        f.write(f"id={r[0]} | {r[2]} - {r[1]}\n")
        f.write(f"  搜索: {url}\n\n")

print(f"已生成 {len(rows)} 条记录")
print("文件: _mbid_remaining.txt")
conn.close()
