"""
Pitchfork → 数据库集成工具
功能：
1. 从 album-tracker 数据库读取专辑列表
2. 搜索 Pitchfork 评分并更新数据库
3. 提取评论正文保存为知识库文档
"""
import json, os, sys, sqlite3, re, urllib.request, ssl, subprocess, time
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

# --- Paths ---
DB_PATH = r"C:\Users\qujt\.qclaw\workspace\_music_latest.db"
PF_DIR = r"C:\Users\qujt\.qclaw\workspace\tasks\pitchfork-expert"
DATA_DIR = os.path.join(PF_DIR, "data")
DOCS_DIR = os.path.join(PF_DIR, "docs", "reviews")
OUTPUT_DIR = os.path.join(PF_DIR, "data", "batch")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml",
}

# --- DB helpers ---
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_albums_without_pf_score(limit=50):
    """Get albums that don't have a pitchfork_score yet."""
    conn = get_db()
    cur = conn.execute("""
        SELECT album_id, album_name, artist, release_year, genre, style
        FROM albums
        WHERE (rym_rating IS NULL AND pitchfork_score IS NULL AND rating IS NULL)
           OR pitchfork_score IS NULL
        ORDER BY album_id DESC
        LIMIT ?
    """, (limit,))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_pf_score(album_id, score, bnm=False, review_url=""):
    conn = get_db()
    conn.execute(
        "UPDATE albums SET pitchfork_score = ?, review_url = ? WHERE album_id = ?",
        (score, review_url, album_id)
    )
    conn.commit()
    conn.close()

# --- Pitchfork Search ---
def pf_search(artist, album):
    """Search Pitchfork for a review, return best match."""
    q = f"{artist} {album}"
    q_encoded = q.replace(" ", "+")
    url = f"https://pitchfork.com/search/?q={q_encoded}"
    
    r = subprocess.run(
        ["curl", "-k", "-s", "-L", url],
        capture_output=True, text=False, timeout=15
    )
    html = r.stdout.decode("utf-8", errors="replace")
    
    # Extract from __PRELOADED_STATE__
    m = re.search(r'window\.__PRELOADED_STATE__\s*=\s*(\{.+?\})\s*;\s*</script>', html, re.DOTALL)
    if not m:
        return None
    
    try:
        state = json.loads(m.group(1))
    except:
        return None
    
    search = state.get("transformed", {}).get("search", {})
    categories = search.get("items", [])
    
    results = []
    for cat in categories:
        for item in cat.get("items", []):
            rv = item.get("ratingValue", {})
            ct = rv.get("channelType", "")
            if item.get("contentType") != "review" or ct != "Albums":
                continue
            hed = re.sub(r'<[^>]+>', '', item.get("dangerousHed", "")).strip()
            subhed = item.get("subHed", {})
            artist_name = subhed.get("name", "")
            review_url = item.get("url", "")
            if not review_url.startswith("http"):
                review_url = f"https://pitchfork.com{review_url}"
            
            results.append({
                "artist": artist_name,
                "album": hed,
                "score": rv.get("score"),
                "bnm": rv.get("isBestNewMusic", False),
                "url": review_url.rstrip("/"),
            })
    
    # Simple matching: prefer exact match
    if results:
        al = album.lower().strip()
        ar = artist.lower().strip()
        for r in results:
            ra = r["artist"].lower().strip()
            rb = r["album"].lower().strip()
            # Check exact match on artist
            if ar in ra or ra in ar:
                if al in rb or rb in al:
                    return r
        # Fallback: first result
        return results[0]
    return None


def fetch_review_detail(url):
    """Fetch full review detail."""
    r = subprocess.run(
        ["curl", "-k", "-s", "-L", url],
        capture_output=True, text=False, timeout=15
    )
    html = r.stdout.decode("utf-8", errors="replace")
    
    m = re.search(r'window\.__PRELOADED_STATE__\s*=\s*(\{.+?\})\s*;\s*</script>', html, re.DOTALL)
    if not m:
        return None
    
    try:
        state = json.loads(m.group(1))
    except:
        return None
    
    review = state.get("transformed", {}).get("review", {})
    header = review.get("headerProps", {})
    info = header.get("infoSliceFields", {})
    artist_list = header.get("artists", [{}])
    
    result = {
        "url": url,
        "album": re.sub(r'<[^>]+>', '', header.get("dangerousHed", "")).strip(),
        "artist": artist_list[0].get("name", "?") if artist_list else "?",
        "score": header.get("musicRating", {}).get("score"),
        "bnm": header.get("musicRating", {}).get("isBestNewMusic", False),
        "label": info.get("label", ""),
        "review_date": info.get("reviewDate", ""),
        "release_year": info.get("releaseYear", ""),
    }
    
    # Extract review body
    body_ir = review.get("body", [])
    result["body_html"] = json.dumps(body_ir) if body_ir else ""
    
    return result


def save_review_md(detail, out_dir=DOCS_DIR):
    """Save review as markdown."""
    slug = detail["url"].rstrip("/").split("/")[-1]
    md = f"# {detail['artist']} — {detail['album']}\n\n"
    md += f"**Score**: {detail['score']}"
    if detail.get('bnm'):
        md += " 🏆 Best New Music"
    md += f"\n\n**Reviewed**: {detail.get('review_date', '')}\n"
    if detail.get('label'):
        md += f"**Label**: {detail['label']}\n"
    if detail.get('release_year'):
        md += f"**Release Year**: {detail['release_year']}\n"
    md += f"**URL**: {detail['url']}\n\n---\n\n"
    md += f"_(Body extraction available via pf_review_body.py)_"
    
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{slug}.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(md)
    return path


def batch_update(limit=20, skip_pf=False):
    """Batch workflow: scan DB → search PF → update → save."""
    albums = get_albums_without_pf_score(limit)
    print(f"[PF Batch] {len(albums)} albums to check")
    
    results = []
    for i, alb in enumerate(albums):
        name = f"{alb['artist']} — {alb['album_name']}"
        year = alb.get("release_year", "")
        print(f"\n[{i+1}/{len(albums)}] {name} ({year})", end="...", flush=True)
        
        pf = pf_search(alb["artist"], alb["album_name"])
        if pf and (isinstance(pf["score"], (int, float)) or pf["url"]):
            print(f" PF={pf.get('score', 'N/A')}, url={pf.get('url', '')[:50]}")
            
            # Update DB
            update_pf_score(
                alb["album_id"],
                pf.get("score"),
                pf.get("bnm", False),
                pf.get("url", ""),
            )
            
            # Save detail
            if pf.get("url"):
                try:
                    detail = fetch_review_detail(pf["url"])
                    if detail and detail.get("score"):
                        path = save_review_md(detail)
                        print(f"   Saved: {path}")
                        results.append(detail)
                except Exception as e:
                    print(f"   Detail error: {e}")
            
            time.sleep(1.5)
        else:
            print(" no PF review found")
        
        results.append({"match": pf, "album": alb})
    
    # Save batch results
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = os.path.join(OUTPUT_DIR, f"batch_{ts}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\n[PF Batch] Saved: {out}")
    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", type=int, default=0, help="Batch update N albums")
    parser.add_argument("--search", nargs=2, metavar=("ARTIST", "ALBUM"), help="Search specific album")
    parser.add_argument("--stats", action="store_true", help="Show PF coverage stats")
    args = parser.parse_args()
    
    if args.stats:
        conn = get_db()
        total = conn.execute("SELECT COUNT(*) FROM albums").fetchone()[0]
        with_pf = conn.execute("SELECT COUNT(*) FROM albums WHERE pitchfork_score IS NOT NULL").fetchone()[0]
        with_pf_year = conn.execute("SELECT COUNT(*) FROM albums WHERE pitchfork_score IS NOT NULL AND release_year >= 2000").fetchone()[0]
        print(f"[PF Stats] Total: {total} | With PF score: {with_pf} | Post-2000: {with_pf_year}")
        conn.close()
    
    if args.batch > 0:
        batch_update(limit=args.batch)
    
    if args.search:
        artist, album = args.search
        print(f"[PF Search] {artist} — {album}")
        result = pf_search(artist, album)
        if result:
            print(f"  URL: {result['url']}")
            print(f"  Score: {result['score']}")
            print(f"  BNM: {result['bnm']}")
        else:
            print("  Not found on Pitchfork")
