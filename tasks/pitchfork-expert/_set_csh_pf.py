"""Set correct PF scores for CSH albums"""
import sqlite3, subprocess, re, json, time
DB_PATH = r"C:\Users\qujt\.qclaw\workspace\_music_latest.db"
conn = sqlite3.connect(DB_PATH)

# Correct CSH albums
csh = {
    323: ("Twin Fantasy", 8.6, "https://pitchfork.com/reviews/albums/car-seat-headrest-twin-fantasy"),
    382: ("Teens of Denial", 8.5, "https://pitchfork.com/reviews/albums/23032-teens-of-denial/"),
    383: ("Nervous Young Man", 8.0, "https://pitchfork.com/reviews/albums/21091-nervous-young-man/"),
    386: ("How to Leave Town", 8.0, "https://pitchfork.com/reviews/albums/21573-how-to-leave-town/"),
}

for aid, (name, score, url) in csh.items():
    conn.execute("UPDATE albums SET pitchfork_score = ?, review_url = ? WHERE album_id = ?",
                 (score, url, aid))
    print(f"  album_id={aid}: {name} — PF={score}")

# Search for Monomania and MADLO scores
for search in ["Monomania", "Making a Door Less Open"]:
    q = f"Car Seat Headrest {search}".replace(" ", "+")
    r = subprocess.run(["curl", "-k", "-s", "-L", f"https://pitchfork.com/search/?q={q}"],
                       capture_output=True, text=False, timeout=15)
    html = r.stdout.decode("utf-8", errors="replace")
    m = re.search(r'window\.__PRELOADED_STATE__\s*=\s*(\{.+?\})\s*;\s*</script>', html, re.DOTALL)
    if m:
        try:
            state = json.loads(m.group(1))
            items = state.get("transformed", {}).get("search", {}).get("items", [])
            for cat in items:
                for item in cat.get("items", []):
                    hed = re.sub(r'<[^>]+>', '', item.get("dangerousHed", "")).strip()
                    if search.lower() in hed.lower():
                        rv = item.get("ratingValue", {})
                        url = item.get("url", "")
                        print(f"  {search}: PF={rv.get('score')}, url={url}")
        except:
            pass
    time.sleep(2)

conn.commit()
conn.close()
