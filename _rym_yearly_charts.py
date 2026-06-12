"""
RYM 年度 Charts 批量抓取 - 完整版
抓取 2020-2025 年度榜 + 新发片 + 收藏差距分析
"""
import json, time, re, os, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BASE = "https://rateyourmusic.com"
PROJECT = r"C:\Users\qujt\.qclaw\workspace\tasks\rym-expert"
os.makedirs(os.path.join(PROJECT, "data", "new-releases"), exist_ok=True)
os.makedirs(os.path.join(PROJECT, "data", "charts-yearly"), exist_ok=True)
os.makedirs(os.path.join(PROJECT, "data", "collection"), exist_ok=True)

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text.strip("-")

def extract_charts(html):
    """Extract chart items from yearly chart HTML."""
    items = []
    idx_positions = [m.start() for m in re.finditer(
        r'class="page_charts_section_charts_item object_release">', html)]
    
    for i, start in enumerate(idx_positions):
        end = idx_positions[i+1] if i+1 < len(idx_positions) else len(html)
        block = html[start:end]
        
        rid_m = re.search(r'page_charts_section_charts_item_(\d+)', block)
        rid = rid_m.group(1) if rid_m else ""
        
        name_ms = re.findall(r'<span class="ui_name_locale_original">([^<]+)</span>', block)
        album = name_ms[0].strip() if len(name_ms) > 0 else ""
        artist = name_ms[1].strip() if len(name_ms) > 1 else ""
        
        if not artist:
            artist_m = re.search(
                r'class="page_charts_section_charts_item_credited_links_primary"[^>]*>.*?'
                r'<span class="ui_name_locale_original">([^<]+)</span>',
                block, re.DOTALL
            )
            artist = artist_m.group(1).strip() if artist_m else ""
        
        rating_m = re.search(
            r'class="page_charts_section_charts_item_details_average_num">([\d.]+)', block)
        count_m = re.search(
            r'class="page_charts_section_charts_item_details_ratings">([\d,]+)', block)
        date_m = re.search(
            r'class="page_charts_section_charts_item_title_date_compact"[^>]*>.*?'
            r'<span>\s*([\d\sA-Za-z]+\d{4})', block, re.DOTALL)
        genres = re.findall(r'class="genre comma_separated[^"]*" href="[^"]+">([^<]+)</a>', block)
        url_m = re.search(r'class="page_charts_section_charts_item_link release" href="([^"]+)"', block)
        url = url_m.group(1).strip() if url_m else ""
        
        if album and artist:
            items.append({
                "release_id": rid, "album": album, "artist": artist,
                "rating": float(rating_m.group(1)) if rating_m else None,
                "ratings": count_m.group(1).strip() if count_m else "",
                "release_date": date_m.group(1).strip() if date_m else "",
                "genres": [g.strip() for g in genres[:3]],
                "rym_url": url if url else f"/release/album/{slugify(artist)}/{slugify(album)}/"
            })
    return items

def extract_new_releases(html):
    """Extract new releases from new-music HTML."""
    items = []
    rid_positions = [(m.start(), m.group(1)) for m in re.finditer(r'release_(\d+)', html)]
    seen = set()
    
    for pos, rid in rid_positions:
        if rid in seen:
            continue
        seen.add(rid)
        
        end = min(len(html), pos + 5000)
        next_rid_pos = html.find('release_', pos + 10)
        if next_rid_pos > 0 and next_rid_pos < end:
            end = next_rid_pos
        
        block = html[max(0, pos-20):end]
        
        title_m = re.search(r'class="album newreleases_item_title"[^>]*title="[^"]*">([^<]+)</a>', block)
        artist_m = re.search(r'<span class="newreleases_item_artist"><a[^>]*class="artist"[^>]*>([^<]+)</a></span>', block)
        rating_m = re.search(r'class="newreleases_stat newreleases_avg_rating_stat">([\d.]+)</span>', block)
        ratings_m = re.search(r'class="newreleases_stat newreleases_ratings_stat">([\d,]+)</span>', block)
        wishlist_m = re.search(r'class="newreleases_stat newreleases_wishlist_stat">([\d,]+)</span>', block)
        date_m = re.search(r'class="newreleases_item_releasedate">([^<]+)</div>', block)
        genre_ms = re.findall(r'<span class="newreleases_item_genres">([^<]+)</span>', block)
        cover_m = re.search(r'class="newreleases_item_art" src="([^"]+)"', block)
        
        title = title_m.group(1).strip() if title_m else ""
        artist = artist_m.group(1).strip() if artist_m else ""
        
        if title and artist:
            slug = slugify(artist) + "/" + slugify(title)
            items.append({
                "release_id": rid, "album": title, "artist": artist,
                "rating": float(rating_m.group(1)) if rating_m else None,
                "ratings": ratings_m.group(1).strip() if ratings_m else "",
                "wishlist": wishlist_m.group(1).strip() if wishlist_m else "",
                "release_date": date_m.group(1).strip() if date_m else "",
                "genres": [g.strip().rstrip(',') for g in genre_ms],
                "cover_url": cover_m.group(1) if cover_m else "",
                "rym_url": f"/release/album/{slug}/"
            })
    return items

def js_nav(page, path):
    page.evaluate(f"window.location.href = '{path}'")
    time.sleep(12)

def main():
    import cloakbrowser
    
    print("1. Launching CloakBrowser...")
    browser = cloakbrowser.launch(headless=False)
    page = browser.new_page()
    
    print("2. Loading RYM home (CF challenge)...")
    page.goto(BASE, wait_until="networkidle", timeout=90000)
    time.sleep(25)
    print(f"   Home: {len(page.content())} chars OK")
    
    # 3. New releases
    print("\n3. New releases...")
    js_nav(page, "/new-music/")
    time.sleep(8)
    releases_html = page.content()
    releases = extract_new_releases(releases_html)
    print(f"   Found {len(releases)} items")
    
    out_releases = os.path.join(PROJECT, "data", "new-releases", "new_releases_20260612.json")
    with open(out_releases, "w", encoding="utf-8") as f:
        json.dump(releases, f, ensure_ascii=False, indent=2)
    
    # 4. Yearly charts 2020-2025
    yearly_pages = [
        ("2025", "/charts/top/album/2025/"),
        ("2024", "/charts/top/album/2024/"),
        ("2023", "/charts/top/album/2023/"),
        ("2022", "/charts/top/album/2022/"),
        ("2021", "/charts/top/album/2021/"),
        ("2020", "/charts/top/album/2020/"),
    ]
    
    all_chart_items = []
    for year, ypath in yearly_pages:
        print(f"\n4. {year} chart...", end=" ", flush=True)
        try:
            js_nav(page, ypath)
            time.sleep(8)
            html = page.content()
            items = extract_charts(html)
            print(f"{len(items)} items", flush=True)
            
            yr_dir = os.path.join(PROJECT, "data", "charts-yearly", year)
            os.makedirs(yr_dir, exist_ok=True)
            out = os.path.join(yr_dir, f"{year}.json")
            with open(out, "w", encoding="utf-8") as f:
                json.dump(items, f, ensure_ascii=False, indent=2)
            
            all_chart_items.extend([{**item, "chart_year": year} for item in items])
        except Exception as e:
            print(f"Error: {e}", flush=True)
    
    # 5. Gap analysis
    print("\n5. Gap analysis...")
    db_path = r"\\10.0.2.4\qemu\原创计划\music\music"
    user_albums = {}
    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            "SELECT album_name, artist, rym_rating FROM albums WHERE rym_rating IS NOT NULL")
        for row in cur.fetchall():
            key = f"{row['artist']}|{row['album_name']}"
            user_albums[key] = row["rym_rating"]
        conn.close()
        print(f"   DB: {len(user_albums)} albums with RYM data")
    except Exception as e:
        print(f"   DB inaccessible: {e}")
    
    high_rated = []
    for item in all_chart_items:
        if item.get("rating") and item["rating"] >= 4.0:
            key = f"{item['artist']}|{item['album']}"
            if key not in user_albums:
                high_rated.append(item)
    
    high_rated.sort(key=lambda x: -x["rating"])
    print(f"   Gap (4.0+): {len(high_rated)} albums")
    
    gap_out = os.path.join(PROJECT, "data", "collection", "gap_highrated_20260612.json")
    with open(gap_out, "w", encoding="utf-8") as f:
        json.dump(high_rated, f, ensure_ascii=False, indent=2)
    
    # Master yearly
    master_out = os.path.join(PROJECT, "data", "charts-yearly", "master_yearly_20260612.json")
    with open(master_out, "w", encoding="utf-8") as f:
        json.dump(all_chart_items, f, ensure_ascii=False, indent=2)
    
    browser.close()
    
    print("\n=== DONE ===")
    print(f"New releases: {len(releases)} items")
    print(f"Yearly charts: {len(all_chart_items)} items (2020-2025)")
    print(f"High-rated gap: {len(high_rated)} albums")
    print("\nTop 20 missing:")
    for item in high_rated[:20]:
        print(f"  [{item['rating']}] {item['artist']} - {item['album']} ({item['chart_year']})")

if __name__ == "__main__":
    main()