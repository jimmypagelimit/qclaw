"""Check false positive PF scores for Chinese artists"""
import sqlite3, json
DB_PATH = r"C:\Users\qujt\.qclaw\workspace\_music_latest.db"
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

suspicious = conn.execute("""
    SELECT album_id, album_name, artist, pitchfork_score, review_url, release_year
    FROM albums 
    WHERE pitchfork_score IS NOT NULL 
    ORDER BY pitchfork_score DESC
""").fetchall()

print("所有有 PF 评分的专辑:")
for r in suspicious:
    # Count Chinese chars in artist + album
    text = f"{r['artist']} {r['album_name']}"
    cn_count = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    flag = " FALSE-POS" if cn_count > 2 else ""
    print(f"  {r['album_id']:4d} | PF={r['pitchfork_score']} | {repr(r['artist'])[:30]:30s} — {repr(r['album_name'])[:40]:40s} | {flag.strip()}")
    if r['review_url']:
        print(f"        url: {r['review_url']}")

conn.close()
