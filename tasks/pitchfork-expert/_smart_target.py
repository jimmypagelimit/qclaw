"""智慧批量：只查询有较高概率被 PF 评论过的专辑（英文名+indie倾向）"""
import sqlite3, json, os, sys, re, subprocess
sys.stdout.reconfigure(encoding="utf-8")

DB_PATH = r"C:\Users\qujt\.qclaw\workspace\_music_latest.db"

# Known PF reviews to add
known = [
    (4, 8.6, "https://pitchfork.com/reviews/albums/car-seat-headrest-twin-fantasy"),    # Twin Fantasy
    (5, 8.5, "https://pitchfork.com/reviews/albums/23032-teens-of-denial/"),            # Teens of Denial
    (348, 8.0, "https://pitchfork.com/reviews/albums/21573-how-to-leave-town/"),        # How to Leave Town
    (3, 8.0, "https://pitchfork.com/reviews/albums/21091-nervous-young-man/"),          # Nervous Young Man - actually id might differ
]

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

# 1. Insert known scores
for album_id, score, url in known:
    conn.execute("UPDATE albums SET pitchfork_score = ?, review_url = ? WHERE album_id = ?",
                 (score, url, album_id))
    print(f"[Known] album_id={album_id}: PF={score}")

# 2. Find English-language indie albums most likely to have PF reviews
rows = conn.execute("""
    SELECT album_id, album_name, artist, release_year 
    FROM albums 
    WHERE pitchfork_score IS NULL 
      AND rym_rating IS NOT NULL 
      AND rym_ratings_count > 500
    ORDER BY rym_ratings_count DESC
    LIMIT 100
""").fetchall()

print(f"\n[Target] {len(rows)} albums with RYM ratings>500 and no PF score\n")

# Show top 20
for r in rows[:20]:
    print(f"  {r['album_id']:4d} | {r['artist'][:20]:20s} — {r['album_name'][:30]:30s} ({r['release_year']})")

conn.commit()
conn.close()
