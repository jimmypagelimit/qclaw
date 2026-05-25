#!/usr/bin/env python3
"""
Search NetEase Cloud Music API for album covers.
Uses public search API - no browser needed.
"""
import sqlite3
import json
import os
import time
import urllib.request
import urllib.parse

DB = "G:/原创计划/music"
COVERS_DIR = r"C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\covers"
PROJECT_DIR = r"C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker"

def search_netease(keyword, limit=5):
    """Search NetEase Cloud Music for albums."""
    url = f"https://music.163.com/api/search/get/web?s={urllib.parse.quote(keyword)}&type=10&offset=0&limit={limit}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Referer": "https://music.163.com/"
    })
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read().decode())
        return data
    except Exception as e:
        return {"error": str(e)}

def get_album_cover(album_name, artist):
    """Search for album and return cover URL."""
    # Try full search first
    keyword = f"{album_name} {artist}"
    data = search_netease(keyword)
    
    if "error" in data:
        return None
    
    try:
        # type=10 returns albums directly in result.albums
        albums = data.get("result", {}).get("albums", [])
        
        if not albums:
            # Try just album name
            data2 = search_netease(album_name)
            albums = data2.get("result", {}).get("albums", [])
        
        for album in albums[:3]:
            cover_url = album.get("picUrl") or album.get("blurPicUrl")
            if cover_url:
                return cover_url
    except:
        pass
    return None

def download_cover(url, filepath):
    """Download cover image to filepath."""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://music.163.com/"
        })
        resp = urllib.request.urlopen(req, timeout=15)
        data = resp.read()
        if len(data) < 1000:
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
    
    log_path = os.path.join(PROJECT_DIR, "netease_dl_log2.txt")
    
    success = 0
    fail = 0
    
    with open(log_path, "w", encoding="utf-8") as log:
        log.write(f"Missing covers: {len(rows)}\n")
        
        for i, (album_id, album_name, artist) in enumerate(rows):
            log.write(f"[{i+1}/{len(rows)}] {artist} - {album_name} ... ")
            
            cover_url = get_album_cover(album_name, artist)
            
            if cover_url:
                filename = f"{album_id}-COV.jpg"
                filepath = os.path.join(COVERS_DIR, filename)
                
                if download_cover(cover_url, filepath):
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
                    log.write(f"OK ({cover_url[:60]})\n")
                else:
                    fail += 1
                    log.write("FAIL (download)\n")
            else:
                fail += 1
                log.write("FAIL (not found)\n")
            
            log.flush()
            time.sleep(0.5)
        
        log.write(f"\nResult: {success} success / {fail} fail / {len(rows)} total\n")
    
    conn.close()
    print(f"Done! {success} success / {fail} fail")

if __name__ == "__main__":
    main()