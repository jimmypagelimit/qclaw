import sqlite3, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
cur = conn.cursor()

# albums missing rym_rating
cur.execute("""
SELECT a.album_id, a.artist, a.album_name, 
       COUNT(l.rowid) as listen_count
FROM albums a
LEFT JOIN listen_history l ON a.album_id = l.album_id
WHERE (a.rym_rating IS NULL OR a.rym_rating = 0)
GROUP BY a.album_id
ORDER BY listen_count DESC, a.artist, a.album_name
LIMIT 50
""")
rows = cur.fetchall()
print(f'=== Missing RYM: top 50 by listen count ===')
for r in rows:
    aid, artist, album, lc = r
    print(f'{aid:<5} {artist:<20} {album:<35} [{lc}x]')

# total missing
cur.execute("SELECT COUNT(*) FROM albums WHERE (rym_rating IS NULL OR rym_rating = 0)")
total = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM albums WHERE rym_rating IS NOT NULL AND rym_rating > 0")
have = cur.fetchone()[0]
print(f'\nMissing: {total} | Have: {have} | Total: {total+have}')
conn.close()
