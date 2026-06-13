"""Fetch review HTML via web_fetch proxy, extract body locally."""
import json, re, sys, os
sys.stdout.reconfigure(encoding="utf-8")

# Read the HTML saved from web_fetch (we'll pipe it through a temp file approach)
# Alternative: use the known URL and fetch via subprocess curl or just parse what we have

url = "https://pitchfork.com/reviews/albums/21673-teens-of-denial/"
print(f"Fetching: {url}")

# Use curl which handles SSL better on Windows
import subprocess
result = subprocess.run(
    ["cmd", "/c", "curl", "-k", "-s", "-L", url,
     "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"],
    capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30
)
html = result.stdout
print(f"HTML size: {len(html)} bytes")

if len(html) < 1000:
    print("ERROR: Too small, probably failed")
    sys.exit(1)

m = re.search(r'window\.__PRELOADED_STATE__\s*=\s*(\{.*?\})\s*;', html, re.DOTALL)
if not m:
    print("No __PRELOADED_STATE__ found")
    sys.exit(1)

data = json.loads(m.group(1))
review = data.get("transformed", {}).get("review", {})
header = review.get("headerProps", {})
info = header.get("infoSliceFields", {})
artist_list = header.get("artists", [{}])

meta = {
    "url": url,
    "album": header.get("dangerousHed", "").replace("<em>", "").replace("</em>", ""),
    "artist": artist_list[0].get("name", "?") if artist_list else "?",
    "score": header.get("musicRating", {}).get("score"),
    "bnm": header.get("musicRating", {}).get("isBestNewMusic", False),
    "author": ", ".join(data.get("coreDataLayer", {}).get("content", {}).get("authorNames", [])),
    "date": info.get("reviewDate", ""),
}

print(f"\n{meta['artist']} — {meta['album']}")
print(f"Score: {meta['score']} | BNM: {meta['bnm']} | {meta['author']} | {meta['date']}")

# Save raw HTML for body extraction
out = r"C:\Users\qujt\.qclaw\workspace\tasks\pitchfork-expert\_tod_raw.html"
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Raw HTML saved to {out}")
