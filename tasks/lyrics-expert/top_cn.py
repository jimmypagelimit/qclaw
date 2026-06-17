import sqlite3
DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("""
    SELECT a.album_id, a.artist, a.album_name,
           (SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id) as pc
    FROM albums a
    WHERE a.album_name != ''
    ORDER BY pc DESC
""")
rows = cur.fetchall()
conn.close()

cn = [(a_id, art, alb, pc) for a_id, art, alb, pc in rows if any('\u4e00' <= c <= '\u9fff' for c in str(art)+str(alb))]
out = f"Chinese albums needing lyrics: {len(cn)}\n"
for a_id, art, alb, pc in cn[:10]:
    out += f"  [{pc:2d}] {repr(art)} - {repr(alb)} (id={a_id})\n"

with open(r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\top_cn.txt', 'w', encoding='utf-8') as f:
    f.write(out)
print(out)
