import sqlite3, json
conn = sqlite3.connect(r"C:\Users\qujt\.qclaw\workspace\_music_latest.db")
c = conn.cursor()
c.execute("""
SELECT a.album_id, a.album_name, a.artist, COUNT(lh.album_id) as cnt
FROM listen_history lh
JOIN albums a ON lh.album_id = a.album_id
WHERE lh.listen_year = 2026
GROUP BY lh.album_id
ORDER BY cnt DESC
LIMIT 10
""")
rows = c.fetchall()
conn.close()

# Write as JSON for clean UTF-8 output
with open("_top2026.json", "w", encoding="utf-8") as f:
    json.dump(rows, f, ensure_ascii=False, indent=2)
print("Done")
