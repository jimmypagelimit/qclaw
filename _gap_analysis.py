import sqlite3
DB = r"C:\Users\qujt\.qclaw\workspace\_music_latest.db"
db = sqlite3.connect(DB)
db.row_factory = sqlite3.Row

missing = db.execute('''
    SELECT a.artist, COUNT(*) as cnt
    FROM tracks t
    JOIN albums a ON t.album_id = a.album_id
    WHERE t.lyrics_lrc_path IS NULL AND t.lyrics_text_path IS NULL
    GROUP BY a.artist
    ORDER BY cnt DESC
    LIMIT 30
''').fetchall()

print("Top 30 artists with missing lyrics:")
for r in missing:
    print(f"  {r['artist']}: {r['cnt']}")
db.close()
