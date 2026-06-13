"""Check PF batch results and find next album to process"""
import sqlite3, json, sys
from datetime import datetime
sys.stdout.reconfigure(encoding="utf-8")

DB_PATH = r"C:\Users\qujt\.qclaw\workspace\_music_latest.db"
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

# Stats
total = conn.execute("SELECT COUNT(*) FROM albums").fetchone()[0]
with_pf = conn.execute("SELECT COUNT(*) FROM albums WHERE pitchfork_score IS NOT NULL").fetchone()[0]
bnm = conn.execute("SELECT COUNT(*) FROM albums WHERE pitchfork_score >= 8.0").fetchone()[0]

print(f"=== PF 评分状态 ({datetime.now().strftime('%H:%M')}) ===")
print(f"总专辑: {total} | 有PF评分: {with_pf} | ≥8.0(BNM): {bnm}")

# Show top scores
import sys
rows = conn.execute("""
    SELECT album_id, album_name, artist, pitchfork_score, review_url, release_year
    FROM albums WHERE pitchfork_score IS NOT NULL
    ORDER BY pitchfork_score DESC
""").fetchall()
print(f"\n按评分降序:")
for r in rows:
    bnm_flag = " BNM" if r['pitchfork_score'] >= 8.0 else ""
    print(f"  {r['pitchfork_score']}{bnm_flag} | {r['artist'][:20]:20s} — {r['album_name'][:30]:30s} ({r['release_year']})")

# Find next English-named album without PF score
print(f"\n接下来还有待搜索的英文艺人专辑:")
remaining = conn.execute("""
    SELECT album_id, album_name, artist, release_year, rym_rating
    FROM albums
    WHERE pitchfork_score IS NULL AND release_year >= 2000
    ORDER BY album_id DESC
""").fetchall()

def is_english(s):
    if not s: return False
    non_ascii = sum(1 for c in s if ord(c) > 127)
    return non_ascii / len(s) < 0.3

english = [r for r in remaining if is_english(r['artist']) and is_english(r['album_name'])]
print(f"  剩余候选: {len(english)} 张")
for r in english[:15]:
    print(f"  {r['album_id']:4d} | {r['artist'][:20]:20s} — {r['album_name'][:35]:35s} ({r['release_year']})")

conn.close()
