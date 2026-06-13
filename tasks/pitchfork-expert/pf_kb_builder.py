"""
Pitchfork 评分知识库生成器
"""
import sqlite3, json, os, glob
from datetime import datetime

DB_PATH = r"C:\Users\qujt\.qclaw\workspace\_music_latest.db"
DOCS_DIR = r"C:\Users\qujt\.qclaw\workspace\tasks\pitchfork-expert\docs"

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # Get all albums with PF scores
    rows = conn.execute("""
        SELECT album_id, album_name, artist, pitchfork_score, review_url, rym_rating, release_year, style
        FROM albums 
        WHERE pitchfork_score IS NOT NULL
        ORDER BY pitchfork_score DESC
    """).fetchall()
    
    conn.close()
    
    print(f"[PF KB] Albums with PF scores: {len(rows)}")
    
    # Build markdown
    md = f"""# Pitchfork 评分知识库

> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}
> 数据源: album-tracker 数据库 (pitchfork_score 字段)

---

## 总览

| 统计项 | 数值 |
|--------|------|
| 已有 PF 评分专辑 | {len(rows)} |
| 最高分 | {max(r['pitchfork_score'] for r in rows)} |
| BNM (≥8.0) | {sum(1 for r in rows if r['pitchfork_score'] >= 8.0)} |
| 平均分 | {sum(r['pitchfork_score'] for r in rows) / len(rows):.2f} |

---\n\n"""
    
    # Group by score range
    ranges = [
        (9.0, 10.0, "9.0–10.0 ⭐⭐⭐ 传世经典"),
        (8.0, 9.0, "8.0–8.9 ⭐⭐ Best New Music"),
        (7.0, 8.0, "7.0–7.9 ⭐ 推荐"),
        (6.0, 7.0, "6.0–6.9 一般"),
        (0.0, 6.0, "0.0–5.9 低分"),
    ]
    
    for lo, hi, label in ranges:
        group = [r for r in rows if lo <= r['pitchfork_score'] < hi]
        if group:
            md += f"## {label} ({len(group)})\n\n"
            for r in group:
                url = r['review_url'] or ""
                rym = f" (RYM: {r['rym_rating']})" if r['rym_rating'] else ""
                year = f" [{r['release_year']}]" if r['release_year'] else ""
                md += f"- **{r['pitchfork_score']}** | {r['artist']} — {r['album_name']}{year}{rym}\n"
                if url:
                    md += f"  - {url}\n"
            md += "\n"
    
    # Save
    path = os.path.join(DOCS_DIR, "PF-SCORES-KB.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"[PF KB] Saved: {path} ({len(md)} chars)")
    
    # Also count reviews with saved body files
    review_dir = os.path.join(DOCS_DIR, "reviews")
    saved = glob.glob(os.path.join(review_dir, "*.md"))
    print(f"[PF KB] Review body files: {len(saved)}")
    
    return md

if __name__ == "__main__":
    main()
