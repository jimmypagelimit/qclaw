"""批量搜索 PF 评分：针对英文艺人+2000年后专辑"""
import sqlite3, json, os, sys, re, subprocess, time
from datetime import datetime
sys.stdout.reconfigure(encoding="utf-8")

DB_PATH = r"C:\Users\qujt\.qclaw\workspace\_music_latest.db"
PF_DIR = r"C:\Users\qujt\.qclaw\workspace\tasks\pitchfork-expert"
DOCS_DIR = os.path.join(PF_DIR, "docs", "reviews")

def is_english(s):
    """Check if string is primarily ASCII/English"""
    if not s: return False
    non_ascii = sum(1 for c in s if ord(c) > 127)
    return non_ascii / len(s) < 0.3

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
    m = re.search(r'window\.__PRELOADED_STATE__\s*=\s*(\{.+?\})\s*;\s*</script>', html, re.DOTALL)
    if not m: return None
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
                "artist": artist_name, "album": hed,
                "score": rv.get("score"), "bnm": rv.get("isBestNewMusic", False),
                "url": review_url.rstrip("/"),
            })
    if results:
        al, ar = album.lower().strip(), artist.lower().strip()
        for r in results:
            ra, rb = r["artist"].lower().strip(), r["album"].lower().strip()
            if ar in ra or ra in ar:
                if al in rb or rb in al:
                    return r
        return results[0]
    return None

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

# Get English-named albums from 2000+, no PF score yet
rows = conn.execute("""
    SELECT album_id, album_name, artist, release_year, rym_rating
    FROM albums 
    WHERE pitchfork_score IS NULL 
      AND release_year >= 2000
    ORDER BY album_id DESC
""").fetchall()
conn.close()

english = [r for r in rows if is_english(r['artist']) and is_english(r['album_name'])]
print(f"[PF Batch] Total candidates: {len(rows)} | English-named: {len(english)}")

# Process first N
limit = min(30, len(english))
hits = 0
for i, r in enumerate(english[:limit]):
    name = f"{r['artist']} — {r['album_name']}"
    print(f"  [{i+1}/{limit}] {r['album_id']:4d} | {r['release_year']} | {name[:60]}", end="...", flush=True)
    
    pf = pf_search(r['artist'], r['album_name'])
    if pf and isinstance(pf.get('score'), (int, float)):
        conn2 = sqlite3.connect(DB_PATH)
        conn2.execute("UPDATE albums SET pitchfork_score = ?, review_url = ? WHERE album_id = ?",
                     (pf['score'], pf.get('url', ''), r['album_id']))
        conn2.commit()
        conn2.close()
        hits += 1
        print(f" PF={pf['score']}" + (" BNM" if pf.get('bnm') else ""))
    elif pf:
        print(f" no-score (url={pf.get('url','')[:30]})")
    else:
        print(" not-found")
    
    if i < limit - 1:
        time.sleep(1.5)

print(f"\n[PF Batch Done] HIT: {hits}/{limit}")

# Refresh stats
conn3 = sqlite3.connect(DB_PATH)
total = conn3.execute("SELECT COUNT(*) FROM albums WHERE pitchfork_score IS NOT NULL").fetchone()[0]
print(f"Total albums with PF score: {total}")
conn3.close()
