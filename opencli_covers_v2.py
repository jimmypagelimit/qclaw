#!/usr/bin/env python3
"""
Cover downloader using opencli + Discogs search.
Strategy: NetEase API -> Discogs (via opencli extract) -> Bandcamp
"""
import sqlite3, json, os, time, subprocess, urllib.request, urllib.parse, re, ssl

DB = "G:/原创计划/music"
COVERS_DIR = r"C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\covers"
LOG_PATH = r"C:\Users\qujt\.qclaw\workspace\opencli_cover_log.txt"

# SSL context that handles Discogs
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

def run_opencli(args, timeout=30):
    cmd = f"opencli {args}"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, encoding='utf-8', errors='replace')
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    except Exception as e:
        return f"ERROR: {e}"

def search_netease_api(album_name, artist):
    """Search NetEase API directly."""
    keyword = f"{album_name} {artist}"
    url = f"https://music.163.com/api/search/get/web?s={urllib.parse.quote(keyword)}&type=10&offset=0&limit=3"
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0", "Referer": "https://music.163.com/"
        })
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode())
        albums = data.get("result", {}).get("albums", [])
        if albums:
            return albums[0].get("picUrl") or albums[0].get("blurPicUrl")
    except:
        pass
    # Try without artist
    url2 = f"https://music.163.com/api/search/get/web?s={urllib.parse.quote(album_name)}&type=10&offset=0&limit=3"
    try:
        req = urllib.request.Request(url2, headers={
            "User-Agent": "Mozilla/5.0", "Referer": "https://music.163.com/"
        })
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode())
        albums = data.get("result", {}).get("albums", [])
        if albums:
            return albums[0].get("picUrl") or albums[0].get("blurPicUrl")
    except:
        pass
    return None

def search_discogs(album_name, artist):
    """Search Discogs via opencli and extract cover URL."""
    keyword = f"{artist} {album_name}"
    search_url = f"https://www.discogs.com/search/?q={urllib.parse.quote(keyword)}&type=release"
    
    output = run_opencli(f'browser work open "{search_url}"', timeout=20)
    time.sleep(2)
    
    extracted = run_opencli("browser work extract", timeout=15)
    
    # Find first image URL (cover art)
    img_pattern = r'!\[[^\]]*\]\((https://i\.discogs\.com/[^)]+)\)'
    matches = re.findall(img_pattern, extracted)
    
    if matches:
        # Upgrade resolution
        url = matches[0]
        url = re.sub(r'h:\d+', 'h:600', url)
        url = re.sub(r'w:\d+', 'w:600', url)
        url = re.sub(r'q:\d+', 'q:90', url)
        return url
    
    # Fallback: search just album name
    search_url2 = f"https://www.discogs.com/search/?q={urllib.parse.quote(album_name)}&type=release"
    run_opencli(f'browser work open "{search_url2}"', timeout=20)
    time.sleep(2)
    extracted2 = run_opencli("browser work extract", timeout=15)
    matches2 = re.findall(img_pattern, extracted2)
    if matches2:
        url = matches2[0]
        url = re.sub(r'h:\d+', 'h:600', url)
        url = re.sub(r'w:\d+', 'w:600', url)
        url = re.sub(r'q:\d+', 'q:90', url)
        return url
    
    return None

def search_bandcamp(album_name, artist):
    """Search Bandcamp via opencli."""
    keyword = f"{artist} {album_name}"
    search_url = f"https://bandcamp.com/search?q={urllib.parse.quote(keyword)}&item_type=a"
    
    run_opencli(f'browser work open "{search_url}"', timeout=20)
    time.sleep(3)
    
    extracted = run_opencli("browser work extract", timeout=15)
    
    # Find album links
    album_pattern = r'href="(https?://[^"]+\.bandcamp\.com/album/[^"]+)"'
    album_links = re.findall(album_pattern, extracted)
    
    if album_links:
        # Visit first album
        run_opencli(f'browser work open "{album_links[0]}"', timeout=20)
        time.sleep(2)
        
        state = run_opencli("browser work state", timeout=15)
        # Find cover image
        cover_pattern = r'src=(https://f4\.bcbits\.com/img/[^\s\]]+)'
        covers = re.findall(cover_pattern, state)
        if covers:
            url = covers[0]
            url = re.sub(r'_\d+\.jpg', '_10.jpg', url)
            return url
    
    return None

def download_image(url, filepath):
    """Download image with SSL workaround."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        resp = urllib.request.urlopen(req, timeout=15, context=ssl_ctx)
        data = resp.read()
        if len(data) < 2000:
            return False
        with open(filepath, "wb") as f:
            f.write(data)
        return True
    except Exception as e:
        # Try without SSL verification
        try:
            resp = urllib.request.urlopen(url, timeout=15, context=ssl_ctx)
            data = resp.read()
            if len(data) < 2000:
                return False
            with open(filepath, "wb") as f:
                f.write(data)
            return True
        except:
            return False

def main():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT album_id, album_name, artist FROM albums WHERE cover_image_url IS NULL OR cover_image_url = ''")
    rows = c.fetchall()
    
    success = 0
    fail_list = []
    
    with open(LOG_PATH, "w", encoding="utf-8") as log:
        log.write(f"Starting cover download for {len(rows)} albums\n")
        log.write(f"Strategy: NetEase API -> Discogs -> Bandcamp\n\n")
        
        for i, (album_id, album_name, artist) in enumerate(rows):
            log.write(f"[{i+1}/{len(rows)}] {artist} - {album_name}\n")
            log.flush()
            
            cover_url = None
            source = None
            
            # Strategy 1: NetEase API (fastest)
            cover_url = search_netease_api(album_name, artist)
            if cover_url:
                source = "netease"
                log.write(f"  Found on NetEase\n")
            
            # Strategy 2: Discogs via opencli
            if not cover_url:
                cover_url = search_discogs(album_name, artist)
                if cover_url:
                    source = "discogs"
                    log.write(f"  Found on Discogs\n")
            
            # Strategy 3: Bandcamp via opencli
            if not cover_url:
                cover_url = search_bandcamp(album_name, artist)
                if cover_url:
                    source = "bandcamp"
                    log.write(f"  Found on Bandcamp\n")
            
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
                    log.write(f"  OK ({source}): saved to {filename}\n\n")
                else:
                    fail_list.append((artist, album_name, "download failed"))
                    log.write(f"  FAIL download: {cover_url[:80]}\n\n")
            else:
                fail_list.append((artist, album_name, "not found"))
                log.write(f"  FAIL not found anywhere\n\n")
            
            log.flush()
            time.sleep(1)
        
        log.write(f"\n=== RESULT ===\n")
        log.write(f"Success: {success}\n")
        log.write(f"Failed: {len(fail_list)}\n")
        for a, n, reason in fail_list:
            log.write(f"  - {a} - {n} ({reason})\n")
    
    conn.close()
    print(f"Done! {success} success / {len(fail_list)} fail")

if __name__ == "__main__":
    main()