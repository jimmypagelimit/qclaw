"""找出还没有歌词的专辑"""
import sqlite3, os

DB = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
LYRICS_DIR = r'C:\Users\qujt\.qclaw\workspace\tasks\lyrics-expert\lyrics'

conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.execute("""
    SELECT a.album_id, a.artist, a.album_name,
           (SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id) as pc
    FROM albums a
    WHERE a.album_name != ''
    ORDER BY pc DESC
    LIMIT 30
""")
rows = cur.fetchall()
conn.close()

print('album_id|artist|album|play_count|has_lyrics')
for album_id, artist, album, pc in rows:
    safe_a = "".join(c for c in artist if c not in r'\/:*?"<>|')
    safe_alb = "".join(c for c in album if c not in r'\/:*?"<>|')
    album_dir = os.path.join(LYRICS_DIR, safe_a, safe_alb)
    has = os.path.exists(album_dir) and any(f.endswith('.lrc') for f in os.listdir(album_dir))
    print(f'{album_id}|{artist}|{album}|{pc}|{"YES" if has else "NO"}')