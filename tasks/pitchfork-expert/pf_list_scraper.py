"""
Pitchfork Expert v3.1 — 年代榜单抓取
从 Pitchfork 的 All-Time / Decade / Year 榜单页面提取数据
"""
import json, re, os, sys, time, subprocess, urllib.request, ssl
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

OUTPUT_DIR = r"C:\Users\qujt\.qclaw\workspace\tasks\pitchfork-expert\data"
DOCS_DIR = r"C:\Users\qujt\.qclaw\workspace\tasks\pitchfork-expert\docs"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

# Use curl via subprocess to avoid SSL issues
def fetch_html(url, timeout=20):
    r = subprocess.run(
        ["curl", "-k", "-s", "-L", url],
        capture_output=True, text=False, timeout=timeout
    )
    return r.stdout.decode("utf-8", errors="replace")


def extract_pf_list(html):
    """Extract album list from best-of or all-time pages.
    Strategy: look for __NEXT_DATA__ or JSON-LD, fallback to regex."""
    entries = []

    # Strategy 1: __NEXT_DATA__
    m = re.search(r'<script id="__NEXT_DATA__".*?>(.*?)</script>', html, re.DOTALL)
    if m:
        try:
            data = json.loads(m.group(1))
            # Navigate: props -> pageProps -> ... -> list items
            pp = data.get("props", {}).get("pageProps", {})
            # Various path possibilities
            for key in ["albums", "items", "reviews", "results"]:
                items = pp.get(key, [])
                if items and isinstance(items, list):
                    for item in items:
                        entry = parse_entry(item)
                        if entry and entry.get("score"):
                            entries.append(entry)
                    if entries:
                        return entries
        except:
            pass

    # Strategy 2: JSON-LD ItemList
    jsonld_blocks = re.findall(
        r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL
    )
    for block in jsonld_blocks:
        try:
            data = json.loads(block)
            if data.get("@type") == "ItemList":
                elements = data.get("itemListElement", [])
                for elem in elements:
                    url = elem.get("url", "")
                    if "/reviews/albums/" in url:
                        entries.append({
                            "name": elem.get("name", "").strip("*").strip(),
                            "url": url.rstrip("/"),
                            "position": elem.get("position", len(entries) + 1),
                        })
                if entries:
                    return entries
        except:
            pass

    # Strategy 3: Regex link extraction
    links = re.findall(
        r'<a[^>]*href="(/reviews/albums/[^"]+)"[^>]*>\s*(.*?)\s*</a>',
        html, re.DOTALL
    )
    seen = set()
    for href, text in links:
        url = f"https://pitchfork.com{href}".rstrip("/")
        if url not in seen:
            seen.add(url)
            name = re.sub(r'<[^>]+>', '', text).strip()
            entries.append({
                "name": name, "url": url,
                "position": len(entries) + 1,
            })

    return entries


def parse_entry(item):
    """Try to parse a content entry from various page structures."""
    if isinstance(item, dict):
        result = {}
        # Path variations
        score = item.get("score") or (item.get("ratingValue") or {}).get("score") if isinstance(item.get("ratingValue"), dict) else item.get("ratingValue")
        result["score"] = score if isinstance(score, (int, float)) else None
        
        hed = re.sub(r'<[^>]+>', '', item.get("dangerousHed", item.get("title", ""))).strip()
        artist = item.get("subHed", {}).get("name", item.get("artist", ""))
        
        result["album"] = hed
        result["artist"] = artist
        result["url"] = item.get("url", "")
        result["bnm"] = item.get("isBestNewMusic", False) or item.get("bnm", False)
        
        return result
    return None


def fetch_list_slug(slug, label=None):
    """Fetch a best-of list by its URL slug."""
    url = f"https://pitchfork.com/{slug}/"
    display = label or slug
    print(f"\n[PF Lists] Fetching: {url}")
    
    html = fetch_html(url)
    entries = extract_pf_list(html)
    print(f"[PF Lists]   Found {len(entries)} entries")
    
    result = {
        "url": url,
        "label": display,
        "slug": slug,
        "fetched_at": datetime.now().isoformat(),
        "entries": entries,
    }
    return result


def fetch_and_save(slug, label=None):
    data = fetch_list_slug(slug, label)
    safe_name = slug.replace("/", "_")
    out = os.path.join(OUTPUT_DIR, f"pf_list_{safe_name}.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[PF Lists] Saved: {out}")
    
    # Generate markdown summary
    md = f"# {data['label']}\n\n{data['url']}\n\n"
    for e in data["entries"]:
        score = f"({e.get('score')})" if e.get("score") else ""
        name = e.get("name") or f"{e.get('artist', '?')} — {e.get('album', '?')}"
        md += f"- {name} {score}\n"
    
    md_file = os.path.join(DOCS_DIR, f"pf_{safe_name}.md")
    with open(md_file, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"[PF Lists] Doc saved: {md_file}")
    return data


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Pitchfork Lists Scraper v3.1")
    parser.add_argument("--slug", help="List slug, e.g. 'best/albums/2024'")
    parser.add_argument("--label", help="Display label")
    parser.add_argument("--batch-best", action="store_true", help="Fetch all 2020-2025 best albums")
    args = parser.parse_args()

    if args.slug:
        data = fetch_and_save(args.slug, args.label)
    elif args.batch_best:
        years = list(range(2020, 2026))
        all_data = {}
        for year in years:
            slug = f"best/albums/{year}"
            data = fetch_and_save(slug, f"Pitchfork Best Albums {year}")
            all_data[year] = data
        
        # Combined summary
        md = "# Pitchfork Best Albums (2020–2025)\n\n"
        for year in years:
            data = all_data.get(year, {})
            md += f"## {year}\n"
            for e in data.get("entries", []):
                score = f"({e.get('score')})" if e.get("score") else ""
                name = e.get("name") or f"{e.get('artist', '?')} — {e.get('album', '?')}"
                md += f"- {name} {score}\n"
            md += "\n"
        
        with open(os.path.join(DOCS_DIR, "pf_best_albums_2020_2025.md"), "w", encoding="utf-8") as f:
            f.write(md)
        print(f"\n[PF Lists] Combined doc: pf_best_albums_2020_2025.md")
    else:
        print("Usage: python pf_list_scraper.py --slug 'best/albums/2024'")
        print("       python pf_list_scraper.py --batch-best")
