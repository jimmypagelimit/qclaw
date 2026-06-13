"""Check why smart_target found 0 albums"""
import sqlite3
DB_PATH = r"C:\Users\qujt\.qclaw\workspace\_music_latest.db"
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

# Check rym_ratings_count distribution
rows = conn.execute("SELECT rym_ratings_count, COUNT(*) as cnt FROM albums GROUP BY rym_ratings_count ORDER BY cnt DESC LIMIT 15").fetchall()
print("rym_ratings_count distribution:")
for r in rows:
    print(f"  {r['rym_ratings_count']}: {r['cnt']} albums")

# Check: albums with rym_rating but no PF and no rym_ratings_count
rows2 = conn.execute("""
    SELECT COUNT(*) FROM albums 
    WHERE pitchfork_score IS NULL 
      AND rym_rating IS NOT NULL 
      AND (rym_ratings_count IS NULL OR rym_ratings_count = 0)
""").fetchone()
print(f"\nAlbums with rym_rating but no rym_ratings_count: {rows2[0]}")

# Check total
total = conn.execute("SELECT COUNT(*) FROM albums WHERE pitchfork_score IS NULL").fetchone()[0]
print(f"Total albums without PF score: {total}")

conn.close()
