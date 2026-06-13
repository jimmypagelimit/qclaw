#!/usr/bin/env python3
"""生成 RYM 知识库文档"""
import sqlite3, json
from pathlib import Path
from datetime import datetime

DB_PATH = Path(r"C:\Users\qujt\.qclaw\workspace\_music_latest.db")
RYM_DIR = Path(r"C:\Users\qujt\.qclaw\workspace\tasks\rym-expert")
DOCS_DIR = RYM_DIR / "docs"

DOCS_DIR.mkdir(parents=True, exist_ok=True)

def build_kb():
    """构建知识库"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # 统计
    stats = {
        'total': conn.execute("SELECT COUNT(*) FROM albums").fetchone()[0],
        'with_rym': conn.execute("SELECT COUNT(*) FROM albums WHERE rym_rating IS NOT NULL").fetchone()[0],
        'with_pf': conn.execute("SELECT COUNT(*) FROM albums WHERE pitchfork_score IS NOT NULL").fetchone()[0],
        'bnm_rym': conn.execute("SELECT COUNT(*) FROM albums WHERE rym_rating >= 4.0").fetchone()[0],
        'bnm_pf': conn.execute("SELECT COUNT(*) FROM albums WHERE pitchfork_score >= 8.0").fetchone()[0],
    }
    
    # RYM 高分榜
    rym_top = conn.execute("""
        SELECT album_name, artist, rym_rating, rym_ratings_count, release_year
        FROM albums
        WHERE rym_rating IS NOT NULL
        ORDER BY rym_rating DESC, rym_ratings_count DESC
        LIMIT 50
    """).fetchall()
    
    # 生成 Markdown
    md = f"""# RYM 知识库

> 更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## 统计

| 指标 | 数量 |
|------|------|
| 总专辑数 | {stats['total']} |
| 有 RYM 评分 | {stats['with_rym']} |
| 有 PF 评分 | {stats['with_pf']} |
| RYM ≥4.0 | {stats['bnm_rym']} |
| PF ≥8.0 | {stats['bnm_pf']} |

## RYM 高分榜 Top 50

| 排名 | 专辑 | 艺人 | 评分 | 评价数 | 年份 |
|------|------|------|------|--------|------|
"""
    for i, r in enumerate(rym_top):
        md += f"| {i+1} | {r['album_name'][:30]} | {r['artist'][:20]} | {r['rym_rating']} | {r['rym_ratings_count'] or '-'} | {r['release_year']} |\n"
    
    # 保存
    out_file = DOCS_DIR / "RYM-KB.md"
    out_file.write_text(md, encoding='utf-8')
    print(f"[RYM KB] 已生成: {out_file}")
    print(f"[RYM KB] 覆盖率: {stats['with_rym']}/{stats['total']} ({100*stats['with_rym']/stats['total']:.1f}%)")
    
    conn.close()

if __name__ == "__main__":
    build_kb()
