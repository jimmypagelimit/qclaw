#!/usr/bin/env python3
"""
Auto-cover downloader using opencli browser automation.
Strategy: NetEase Cloud -> Bandcamp -> Discogs (via Google image search)
"""
import sqlite3, json, os, time, subprocess, urllib.request, re

DB = "G:/原创计划/music"
COVERS_DIR = r"C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\covers"
LOG_PATH = r"C:\Users\qujt\.qclaw\workspace\opencli_cover_log.txt"

def run_opencli(args, timeout=30):
    """Run opencli command and return output."""
    cmd = f"opencli {args}"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    except Exception as e:
        return f"ERROR: {e}"

def search_netease_extract(album_name, artist):
    """Search NetEase and extract cover URL via opencli."""
    keyword = f"{artist} {album_name}"
    # Use API directly - faster and more reliable
    url = f"https://music.163.com/api/search/get/web?s={urllib.parse.quote(keyword)}&type=10&offset=0&limit=3"
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Referer": "https://music.163.com/"
        })
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode())
        albums = data.get("result", {}).get("albums", [])
        if albums:
            return albums[0].get("picUrl") or albums[0].get("blurPicUrl")
    except:
        pass
    return None

def search_google_images(album_name, artist):
    """Search Google Images via opencli and extract cover URL."""
    keyword = f"{artist} {album_name} album cover"
    search_url = f"https://www.google.com/search?q={urllib.parse.quote(keyword)}&tbm=isch&udm=2"
    
    output = run_opencli(f'browser work open "{search_url}"')
    time.sleep(2)
    
    # Get page state to find image URLs
    state = run_opencli("browser work state")
    
    # Extract image URLs from state
    img_urls = re.findall(r'src=(https?://[^ \s\]]+\.jpe?g[^ \s\]]*)', state)
    if not img_urls:
        img_urls = re.findall(r'(https?://[^ \s\]"\']+\.(?:jpe?g|png|webp)[^ \s\]"\']*)', state)
    
    if img_urls:
        return img_urls[0]
    return None

def search_bandcamp(album_name, artist):
    """Search Bandcamp for album cover."""
    keyword = f"{artist} {album_name}"
    search_url = f"https://bandcamp.com/search?q={urllib.parse.quote(keyword)}&item_type=a"
    
    output = run_opencli(f'browser work open "{search_url}"')
    time.sleep(3)
    
    # Extract page content
    state = run_opencli("browser work state")
    
    # Find album links
    album_links = re.findall(r'href=(https?://[^ \s\]]+\.bandcamp\.com/album/[^ \s\]]+)', state)
    
    if album_links:
        # Visit first album page
        album_url = album_links[0]
        run_opencli(f'browser work open "{album_url}"')
        time.sleep(2)
        
        # Extract cover image from album page
        state2 = run_opencli("browser work state")
        cover_urls = re.findall(r'src=(https?://f4\.bcbits\.com/img/[^ \s\]]+)', state2)
        if cover_urls:
            # Get full-res version (replace _XX.jpg with _10.jpg)
            url = cover_urls[0]
            url = re.sub(r'_\d+\.jpg', '_10.jpg', url)
            return url
    
    return None

def download_image(url, filepath):
    """Download image to filepath."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        resp = urllib.request.urlopen(req, timeout=15)
        data = resp.read()
        if len(data) < 2000:
            return False
        with open(filepath, "wb") as f:
            f.write(data)
        return True
    except Exception as e:
        return False

def main():
    import urllib.parse
    
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT album_id, album_name, artist FROM albums WHERE cover_image_url IS NULL OR cover_image_url = ''")
    rows = c.fetchall()
    
    success = 0
    fail_list = []
    
    with open(LOG_PATH, "w", encoding="utf-8") as log:
        log.write(f"Starting cover download for {len(rows)} albums\n\n")
        
        for i, (album_id, album_name, artist) in enumerate(rows):
            log.write(f"[{i+1}/{len(rows)}] {artist} - {album_name}\n")
            log.flush()
            
            cover_url = None
            source = None
            
            # Strategy 1: NetEase API
            cover_url = search_netease_extract(album_name, artist)
            if cover_url:
                source = "netease"
            
            # Strategy 2: Bandcamp (for indie/underground)
            if not cover_url:
                cover_url = search_bandcamp(album_name, artist)
                if cover_url:
                    source = "bandcamp"
            
            # Strategy 3: Google Images
            if not cover_url:
                cover_url = search_google_images(album_name, artist)
                if cover_url:
                    source = "google"
            
            if cover_url:
                filename = f"{album_id}-COV.jpg"
                filepath = os.path.join(COVERS_DIR, filename)
                
                if download_image(cover_url, filepath):
                    c.execute("UPDATE albums SET cover_image_url = ? WHERE album_id = ?",
                             (f"/covers/{filename}", album_id))
                    for yt in ['albums_2024', 'albums_2025', 'albums_2026']:
                        try:
                            c.execute(f"UPDATE {yt} SET cover_image_url = ? WHERE album_id = ?",
                                     (f"/covers/{filename}", album_id))
                        except:
                            pass
                    conn.commit()
                    success += 1
                    log.write(f"  OK ({source}): {cover_url[:80]}\n\n")
                else:
                    fail_list.append(f"{artist} - {album_name}")
                    log.write(f"  FAIL download: {cover_url[:80]}\n\n")
            else:
                fail_list.append(f"{artist} - {album_name}")
                log.write(f"  FAIL not found\n\n")
            
            log.flush()
            time.sleep(1)
        
        log.write(f"\n=== RESULT ===\n")
        log.write(f"Success: {success}\n")
        log.write(f"Failed: {len(fail_list)}\n")
        for f in fail_list:
            log.write(f"  - {f}\n")
    
    conn.close()
    print(f"Done! {success} success / {len(fail_list)} fail")

if __name__ == "__main__":
    main()