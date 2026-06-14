#!/usr/bin/env python3
"""查询有 PF 评分的专辑"""
import sqlite3
from pathlib import Path

DB = Path(r"C:\Users\qujt\.qclaw\workspace\_music_latest.db")
REVIEWS_DIR = Path(r"C:\Users\qujt\.qclaw\workspace\tasks\pitchfork-expert\docs\reviews")

conn = sqlite3.connect(DB)
rows = conn.execute("""
    SELECT album_id, album_name, artist, pitchfork_score
    FROM albums
    WHERE pitchfork_score IS NOT NULL
    ORDER BY pitchfork_score DESC
""").fetchall()

print(f"=== 有 PF 评分的专辑（{len(rows)} 张）===\n")
print(f"{'id':>4s} | {'评分':>4s} | {'艺人':20s} | 专辑")
print("-" * 80)

for r in rows:
    album_id, album_name, artist, score = r
    # 检查是否已有评论文件
    review_file = REVIEWS_DIR / f"{album_id}_{artist.replace(' ', '_')}_{album_name.replace(' ', '_')[:20]}.md"
    has_review = "[Y]" if review_file.exists() else "[N]"
    print(f"{album_id:4d} | {score:4.1f} | {artist[:20]:20s} | {album_name[:35]} {has_review}")
