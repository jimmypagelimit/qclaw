#!/usr/bin/env python3
"""
Fix remaining 13 covers using opencli screenshot.
Discogs found them but SSL download failed - use browser screenshot instead.
"""
import sqlite3, os, time, subprocess, re

DB = "G:/原创计划/music"
COVERS_DIR = r"C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\covers"
LOG_PATH = r"C:\Users\qujt\.qclaw\workspace\opencli_cover_fix_log.txt"

# Albums that Discogs found but couldn't download
DISCOGS_ALBUMS = [
    ("111", "假假条", "时代在召唤"),
    ("155", "郑钧", "郑钧=zj"), 
    ("156", "苍蝇", "The Fly II"),
    ("157", "黑麒麟", "金陵祭"),
    ("162", "刀郎", "喀什科尔胡杨"),
    ("166", "Nokturnal Mortum", "Голос сталі"),
    ("174", "装咖人", "夜官巡场"),
    ("176", "张福全", "Tea with Flower Fragrance"),
    ("186", "海朋森", "She Came Back From the Square"),
    # ("188", "海朋森", "我不要别的历史"),  # not found
    # ("196", "许巍", "每一刻都是崭新的"),  # not found
]

def run_opencli(args, timeout=30):
    cmd = f"opencli {args}"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout, encoding='utf-8', errors='replace')
        return result.stdout
    except:
        return ""

def search_and_screenshot(album_name, artist):
    """Search Discogs and take screenshot of cover."""
    keyword = f"{artist} {album_name}"
    search_url = f"https://www.discogs.com/search/?q={keyword}&type=release"
    
    # Open search page
    run_opencli(f'browser work open "{search_url}"', timeout=25)
    time.sleep(3)
    
    # Get first result link
    state = run_opencli("browser work state", timeout=15)
    
    # Find first release link
    link_pattern = r'href=(https://www\.discogs\.com/release/\d+-[^"\s]+)'
    links = re.findall(link_pattern, state)
    
    if links:
        # Click on first result
        run_opencli(f'browser work open "{links[0]}"', timeout=25)
        time.sleep(3)
        
        # Get page state to find cover image
        state2 = run_opencli("browser work state", timeout=15)
        
        # Extract image URL and click on it to see full resolution
        img_link_pattern = r'<a href="(https://i\.discogs\.com/[^"]+)"'
        img_links = re.findall(img_link_pattern, state2)
        
        if img_links:
            # Try to get high-res by modifying URL pattern
            # Click on the image (usually first .release-thumb or similar)
            img_click = re.findall(r'<img[^>]+src=(https://i\.discogs\.com[^>\s]+)', state2)
            if not img_click:
                # Try to find any discogs image
                img_click = re.findall(r'src="(https://i\.discogs\.com[^"]+\.jpeg[^"]*)"', state2)
            
            if img_click:
                # Take screenshot of the image
                screenshot_cmd = 'browser work screenshot --full-page'
                output = run_opencli(screenshot_cmd, timeout=30)
                return output
    
    return None

def main():
    success = 0
    fail_list = []
    
    with open(LOG_PATH, "w", encoding="utf-8") as log:
        log.write(f"Fixing {len(DISCOGS_ALBUMS)} remaining covers via screenshot\n\n")
        
        for i, (album_id, artist, album_name) in enumerate(DISCOGS_ALBUMS):
            log.write(f"[{i+1}/{len(DISCOGS_ALBUMS)}] {artist} - {album_name}\n")
            log.flush()
            
            # Search Discogs and take screenshot
            result = search_and_screenshot(album_name, artist)
            
            if result and "screenshot" in result.lower():
                filename = f"{album_id}-COV.jpg"
                filepath = os.path.join(COVERS_DIR, filename)
                
                # Save screenshot (already saved by opencli)
                # Actually opencli saves to temp file - we need to move it
                # Let's check where screenshot was saved
                result2 = run_opencli("browser work screenshot", timeout=15)
                # Look for saved path in output
                path_match = re.search(r'(C:[^\s]+\.png)', result2)
                if path_match:
                    temp_file = path_match.group(1)
                    if os.path.exists(temp_file):
                        os.rename(temp_file, filepath)
                        success += 1
                        log.write(f"  OK: saved to {filename}\n\n")
                    else:
                        fail_list.append((artist, album_name))
                        log.write(f"  FAIL: screenshot not found\n\n")
                else:
                    fail_list.append((artist, album_name))
                    log.write(f"  FAIL: no path in output\n\n")
            else:
                fail_list.append((artist, album_name))
                log.write(f"  FAIL: could not take screenshot\n\n")
            
            log.flush()
            time.sleep(1)
        
        log.write(f"\n=== RESULT ===\n")
        log.write(f"Success: {success}\n")
        log.write(f"Failed: {len(fail_list)}\n")
    
    print(f"Done! {success} success / {len(fail_list)} fail")

if __name__ == "__main__":
    main()