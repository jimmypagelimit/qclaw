"""Set MADLO and Monomania PF scores"""
import sqlite3, subprocess, re, json, time

DB_PATH = r"C:\Users\qujt\.qclaw\workspace\_music_latest.db"
conn = sqlite3.connect(DB_PATH)

# MADLO - known from search
conn.execute("UPDATE albums SET pitchfork_score = 6.6, review_url = ? WHERE album_id = 384",
    ('https://pitchfork.com/reviews/albums/car-seat-headrest-making-a-door-less-open/',))
print("MADLO: PF=6.6")

# Search Monomania
r = subprocess.run(["curl", "-k", "-s", "-L", "https://pitchfork.com/search/?q=Car+Seat+Headrest+Monomania"],
    capture_output=True, text=False, timeout=15)
html = r.stdout.decode("utf-8", errors="replace")
m = re.search(r"window\.__PRELOADED_STATE__\s*=\s*(\{.+?\})\s*;\s*</script>", html, re.DOTALL)
if m:
    state = json.loads(m.group(1))
    items = state.get("transformed", {}).get("search", {}).get("items", [])
    for cat in items:
        for item in cat.get("items", []):
            hed = re.sub(r"<[^>]+>", "", item.get("dangerousHed", "")).strip()
            rv = item.get("ratingValue", {})
            if "monomania" in hed.lower():
                print(f"Monomania: PF={rv.get('score')}")
                if isinstance(rv.get("score"), (int, float)):
                    url = item.get("url", "")
                    if not url.startswith("http"):
                        url = "https://pitchfork.com" + url
                    conn.execute("UPDATE albums SET pitchfork_score = ?, review_url = ? WHERE album_id = 59",
                        (rv["score"], url))
                break
else:
    print("Monomania: search failed")

conn.commit()
conn.close()

# Final state
conn2 = sqlite3.connect(DB_PATH)
total = conn2.execute("SELECT COUNT(*) FROM albums WHERE pitchfork_score IS NOT NULL").fetchone()[0]
print(f"Total with PF score: {total}")
conn2.close()
