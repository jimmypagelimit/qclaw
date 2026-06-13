"""
Pitchfork Expert v3.0 — 基于 __PRELOADED_STATE__ 的专辑评论抓取
数据源: window.__PRELOADED_STATE__ (纯 HTTP，无需浏览器渲染)
已验证字段: score, BNM/BNR, artist, album, genre, label, reviewDate, releaseYear, author, dek
"""
import urllib.request, json, re, html as htmlmod, os, sys, time, argparse
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

OUTPUT_DIR = r"C:\Users\qujt\.qclaw\workspace\tasks\pitchfork-expert\data"
os.makedirs(OUTPUT_DIR, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def fetch_html(url, timeout=15):
    req = urllib.request.Request(url, headers=HEADERS)
    resp = urllib.request.urlopen(req, timeout=timeout)
    return resp.read().decode("utf-8", errors="replace")


def extract_preloaded_state(html):
    """Extract window.__PRELOADED_STATE__ JSON from page HTML."""
    m = re.search(
        r'window\.__PRELOADED_STATE__\s*=\s*(\{.+?\})\s*;?\s*</script>',
        html, re.DOTALL
    )
    if not m:
        return None
    try:
        return json.loads(m.group(1))
    except json.JSONDecodeError:
        # Try fixing truncated JSON — sometimes the last } is missing
        raw = m.group(1)
        if not raw.rstrip().endswith("}"):
            return json.loads(raw + "}")
        raise


def parse_review_detail(html, url):
    """Parse a Pitchfork album review page using __PRELOADED_STATE__."""
    result = {
        "url": url, "album": None, "artist": None,
        "pitchfork_score": None, "reader_score": None, "reader_count": None,
        "genre": None, "genres": [], "label": None, "release_year": None,
        "review_date": None, "author": None, "author_names": [],
        "bnm": False, "bnr": False, "dek": None,
        "image_url": None, "publish_date": None, "content_title": None,
    }

    state = extract_preloaded_state(html)
    if not state:
        return result

    t = state.get("transformed", {})
    review = t.get("review", {})
    hdr = review.get("headerProps", {})
    mhdr = review.get("multiReviewHeaderProps", {})
    info = hdr.get("infoSliceFields", {}) or mhdr.get("infoSliceFields", {})
    mr = hdr.get("musicRating", {}) or (mhdr.get("itemsReviewed", [{}])[0].get("musicRating", {}))

    # Score
    result["pitchfork_score"] = mr.get("score")

    # BNM / BNR
    result["bnm"] = mr.get("isBestNewMusic", False)
    result["bnr"] = mr.get("isBestNewReissue", False)

    # Genre — from infoSliceFields or artists[].genres
    genre = info.get("genre", "")
    if genre:
        result["genre"] = genre
        result["genres"] = [g.strip() for g in genre.split("/")]
    elif artists and artists[0].get("genres"):
        result["genres"] = [g["node"]["name"] for g in artists[0]["genres"]]    
        result["genre"] = ", ".join(result["genres"])

    # Label
    result["label"] = info.get("label")

    # Dates
    result["review_date"] = info.get("reviewDate")
    result["release_year"] = info.get("releaseYear")
    result["publish_date"] = hdr.get("publishDate")

    # Author(s) from coreDataLayer
    cdl = t.get("coreDataLayer", {}).get("content", {})
    author_names = cdl.get("authorNames", "")
    if author_names:
        result["author_names"] = [a.strip() for a in author_names.split(",")]
        result["author"] = result["author_names"][0]

    # Dek (review summary)
    result["dek"] = hdr.get("dangerousDek") or mhdr.get("dangerousDek")

    # Artist — from headerProps.artists (v3.0: correct path)
    artists = hdr.get("artists", [])
    if artists:
        result["artist"] = artists[0].get("name")
    else:
        # Fallback: from multiReviewHeaderProps.artistDetails or title
        ad = mhdr.get("artistDetails", [])
        if ad:
            result["artist"] = ad[0].get("name")

    # Album name — from dangerousHed (strip HTML tags) or contentTitle
    hed = hdr.get("dangerousHed", "") or mhdr.get("dangerousDek", "")
    album_name = re.sub(r'<[^>]+>', '', hed).strip() if hed else ""
    if album_name:
        result["album"] = album_name
    else:
        content_title = cdl.get("contentTitle", "")
        result["content_title"] = content_title
        if content_title:
            result["album"] = content_title

    # Image URL from JSON-LD
    jsonld = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL)
    for block in jsonld:
        try:
            data = json.loads(block)
            item = data.get("itemReviewed", {})
            img = item.get("image", {})
            if isinstance(img, dict):
                result["image_url"] = img.get("url")
            elif isinstance(img, str):
                result["image_url"] = img
        except:
            pass

    return result


def parse_search_results(html):
    """Parse Pitchfork search results from __PRELOADED_STATE__.
    Returns album review links and quick summary data.
    """
    state = extract_preloaded_state(html)
    if not state:
        return []
    
    search = state.get("transformed", {}).get("search", {})
    categories = search.get("items", [])
    
    reviews = []
    for cat in categories:
        # Only extract album reviews (Category 1, contentType=review, channelType=Albums)
        for item in cat.get("items", []):
            rv = item.get("ratingValue", {})
            ct = rv.get("channelType", "")
            if item.get("contentType") != "review":
                continue
            if ct == "Albums":
                hed = re.sub(r'<[^>]+>', '', item.get("dangerousHed", "")).strip()
                dek = item.get("dangerousDek", "")
                subhed = item.get("subHed", {})
                artist = subhed.get("name", "")
                url = item.get("url", "")
                if not url.startswith("http"):
                    url = f"https://pitchfork.com{url}"
                url = url.rstrip("/")
                
                author_items = item.get("contributors", {}).get("author", {}).get("items", [])
                author = author_items[0].get("name", "") if author_items else ""
                
                reviews.append({
                    "name": f"{artist} - {hed}" if artist else hed,
                    "url": url,
                    "artist": artist,
                    "album": hed,
                    "pitchfork_score": rv.get("score") if isinstance(rv.get("score"), (int, float)) else None,
                    "bnm": rv.get("isBestNewMusic", False),
                    "bnr": rv.get("isBestNewReissue", False),
                    "review_date": item.get("date", ""),
                    "author": author,
                    "dek": dek,
                    "position": len(reviews) + 1,
                })
    return reviews


def parse_album_list(html):
    """Parse album list page — extract review links from JSON-LD ItemList.
    Falls back to regex link extraction.
    """
    reviews = []
    jsonld_blocks = re.findall(
        r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL
    )
    for block in jsonld_blocks:
        try:
            data = json.loads(block)
            if data.get("@type") == "ItemList":
                for item in data.get("itemListElement", []):
                    url = item.get("url", "")
                    if "/reviews/albums/" in url:
                        name = item.get("name", "").strip("*").strip()
                        reviews.append({
                            "name": name, "url": url.rstrip("/"),
                            "position": item.get("position", 0),
                        })
                break
        except:
            pass

    if not reviews:
        links = re.findall(
            r'href="(https://pitchfork\.com/reviews/albums/[^"]+)"', html
        )
        seen = set()
        for url in links:
            url = url.rstrip("/")
            if url not in seen and "/reviews/albums/" in url:
                seen.add(url)
                slug = url.split("/")[-1]
                name_parts = slug.replace("-", " ").title()
                reviews.append({"name": name_parts, "url": url, "position": len(reviews) + 1})

    return reviews


def fetch_and_parse_review(url):
    """Fetch a review page and return parsed data."""
    try:
        html = fetch_html(url, timeout=15)
        return parse_review_detail(html, url)
    except Exception as e:
        return {"url": url, "error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Pitchfork Album Review Scraper v3.0")
    parser.add_argument("--pages", type=int, default=1, help="Number of list pages to scrape")
    parser.add_argument("--url", default="https://pitchfork.com/reviews/albums/", help="List page URL")
    parser.add_argument("--search", help="Search query (e.g. 'Car Seat Headrest')")
    parser.add_argument("--limit", type=int, default=10, help="Max reviews to fetch details for")
    parser.add_argument("--list-only", action="store_true", help="Only fetch list, no detail pages")
    parser.add_argument("--type", default="albums", choices=["albums", "tracks", "all"], help="Search result type filter")
    parser.add_argument("--output", default=None, help="Output JSON filename")
    args = parser.parse_args()

    print("[PF v3.0] Pitchfork Album Review Scraper")
    print(f"[PF v3.0] Source: {'Search: ' + args.search if args.search else args.url}")

    # Step 1: Fetch list page(s)
    all_reviews = []
    for page_num in range(1, args.pages + 1):
        if args.search:
            q = args.search.replace(" ", "+")
            list_url = f"https://pitchfork.com/search/?q={q}&page={page_num}"
        else:
            list_url = args.url if page_num == 1 else f"{args.url}?page={page_num}"

        print(f"\n[PF v3.0] List page {page_num}: {list_url}")
        try:
            html = fetch_html(list_url)
            if args.search:
                reviews = parse_search_results(html)
            else:
                reviews = parse_album_list(html)
            print(f"[PF v3.0]   Found {len(reviews)} reviews")
            all_reviews.extend(reviews)
        except Exception as e:
            print(f"[PF v3.0]   Error: {e}")

    if not all_reviews:
        print("[PF v3.0] No reviews found!")
        return

    # Deduplicate by URL
    seen = set()
    unique_reviews = []
    for r in all_reviews:
        if r["url"] not in seen:
            seen.add(r["url"])
            unique_reviews.append(r)

    print(f"[PF v3.0] Total unique reviews: {len(unique_reviews)}")

    if args.list_only:
        for r in unique_reviews:
            print(f"  {r['position']}. {r['name'][:60]}")
        return

    # Step 2: Fetch detail pages
    limit = min(args.limit, len(unique_reviews))
    print(f"\n[PF v3.0] Fetching details for {limit} reviews...")

    details = []
    for i, rev in enumerate(unique_reviews[:limit]):
        print(f"  [{i+1}/{limit}] {rev['name'][:50]}...", end="", flush=True)
        try:
            detail = fetch_and_parse_review(rev["url"])
            detail["position"] = rev["position"]
            if detail.get("error"):
                print(f" ERROR: {detail['error'][:60]}")
            else:
                pf = detail.get("pitchfork_score") or "N/A"
                bnm = " BNM" if detail.get("bnm") else ""
                artist = (detail.get("artist") or "?")[:20]
                album = (detail.get("album") or rev["name"])[:35]
                print(f" PF={pf}{bnm} | {artist} - {album}")
            details.append(detail)
        except Exception as e:
            print(f" ERROR: {e}")
            details.append({"url": rev["url"], "name": rev["name"], "error": str(e)})

        # Rate limit
        if i < limit - 1:
            time.sleep(1)

    # Step 3: Save
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_file = args.output or os.path.join(OUTPUT_DIR, f"pf_reviews_{ts}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(details, f, ensure_ascii=False, indent=2)

    # Summary
    scored = [d for d in details if d.get("pitchfork_score")]
    bnm = [d for d in details if d.get("bnm")]
    errors = [d for d in details if d.get("error")]

    print(f"\n[PF v3.0] Done!")
    print(f"  Saved: {out_file}")
    print(f"  Total: {len(details)} | Scored: {len(scored)} | BNM: {len(bnm)} | Errors: {len(errors)}")

    if scored:
        print(f"\n[PF v3.0] Top scores:")
        for d in sorted(scored, key=lambda x: float(x["pitchfork_score"]), reverse=True)[:10]:
            artist = (d.get("artist") or "?")[:20]
            album = (d.get("album") or "?")[:30]
            print(f"  {d['pitchfork_score']} | {artist} - {album}")


if __name__ == "__main__":
    main()
