#!/usr/bin/env python3
"""
L 项目 - 歌词获取管道 v2
流程：Playwright(MusicBrainz曲目表) -> LRCLIB(歌词) -> 本地保存
"""
import json, sys, os, time, urllib.request, urllib.parse

LRCLIB_BASE = "https://lrclib.net/api"
UA = "AlbumTracker/1.0 (jim@example.com)"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LYRICS_DIR = os.path.join(BASE_DIR, "lyrics")
TRACKLISTS_DIR = os.path.join(BASE_DIR, "tracklists")

os.makedirs(LYRICS_DIR, exist_ok=True)
os.makedirs(TRACKLISTS_DIR, exist_ok=True)

# ===== MusicBrainz via Playwright =====

def mb_get_tracklist(artist, album):
    """用 Playwright 从 MusicBrainz 获取曲目列表"""
    from playwright.sync_api import sync_playwright
    from urllib.parse import quote
    
    with sync_playwright() as p:
        # MusicBrainz 无 CF 保护，可用 headless=True
        browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
        page = browser.new_page()
        
        try:
            # Step 1: 搜索
            search_url = f"https://musicbrainz.org/search?query={quote(artist)}+{quote(album)}&type=release_group&method=indexed"
            print(f"[1] MB Search: {artist} - {album}")
            page.goto(search_url, timeout=30000, wait_until='domcontentloaded')
            page.wait_for_timeout(3000)
            
            rows = page.query_selector_all('table.tbl tbody tr')
            candidates = []
            for row in rows:
                cells = row.query_selector_all('td')
                if len(cells) >= 3:
                    link = cells[0].query_selector('a')
                    type_text = cells[2].inner_text().strip()
                    if link:
                        title = link.inner_text().strip()
                        href = link.get_attribute('href')
                        score = 0
                        if 'Album' in type_text: score += 100
                        if 'Demo' in type_text: score -= 50
                        if 'Remix' in type_text: score -= 50
                        if 'Single' in type_text: score -= 30
                        if album.lower() in title.lower(): score += 20
                        candidates.append((score, href, title, type_text))
            
            if not candidates:
                print("    [X] No results")
                return None
            
            candidates.sort(key=lambda x: x[0], reverse=True)
            best = candidates[0]
            rg_url = f"https://musicbrainz.org{best[1]}" if best[1].startswith('/') else best[1]
            print(f"    Select: {best[2]} [{best[3]}]")
            
            # Step 2: 找 release
            print(f"\n[2] MB Release-group page")
            page.goto(rg_url, timeout=30000, wait_until='domcontentloaded')
            page.wait_for_timeout(3000)
            
            release_table = page.query_selector('table.tbl.mergeable-table')
            if not release_table:
                release_table = page.query_selector('table.tbl')
            
            releases = []
            if release_table:
                for row in release_table.query_selector_all('tr'):
                    cells = row.query_selector_all('td')
                    if len(cells) >= 4:
                        link = cells[0].query_selector('a')
                        fmt = cells[2].inner_text().strip() if len(cells) > 2 else ''
                        tracks_text = cells[3].inner_text().strip() if len(cells) > 3 else ''
                        if link:
                            href = link.get_attribute('href') or ''
                            if href.endswith('/cover-art'):
                                href = href[:-10]
                            if '/release/' in href:
                                releases.append({'href': href, 'format': fmt, 'tracks': tracks_text})
            
            # 选 Digital Media
            target = None
            for r in releases:
                if 'Digital' in r['format']:
                    target = r
                    break
            if not target and releases:
                target = releases[0]
            
            if not target:
                print("    [X] No release")
                return None
            
            print(f"    Choose: {target['format']} (tracks={target['tracks']})")
            
            # Step 3: 提取曲目
            release_url = f"https://musicbrainz.org{target['href']}" if target['href'].startswith('/') else target['href']
            print(f"\n[3] MB Extract tracklist")
            page.goto(release_url, timeout=30000, wait_until='domcontentloaded')
            page.wait_for_timeout(3000)
            
            tracks = []
            for tbl in page.query_selector_all('table.tbl.medium'):
                for row in tbl.query_selector_all('tr'):
                    cells = row.query_selector_all('td')
                    if len(cells) >= 4:
                        pos_text = cells[0].inner_text().strip()
                        try:
                            pos = int(pos_text)
                        except ValueError:
                            continue
                        title_link = cells[1].query_selector('a')
                        title = title_link.inner_text().strip() if title_link else cells[1].inner_text().strip().split('\n')[0].strip()
                        length_text = cells[3].inner_text().strip()
                        dur_ms = 0
                        if ':' in length_text:
                            parts = length_text.split(':')
                            try:
                                dur_ms = (int(parts[0]) * 60 + int(parts[1])) * 1000
                            except ValueError:
                                pass
                        tracks.append({'position': pos, 'title': title, 'duration_ms': dur_ms})
            
            print(f"    {len(tracks)} tracks:")
            for t in tracks:
                dur = f"{t['duration_ms']//1000}s" if t['duration_ms'] else "?"
                print(f"      {t['position']:2d}. {t['title']} ({dur})")
            
            return tracks
            
        finally:
            browser.close()

# ===== LRCLIB =====

def lrclib_search(artist, track, timeout=15):
    params = urllib.parse.urlencode({'q': f'{artist} {track}'})
    url = f"{LRCLIB_BASE}/search?{params}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"      LRCLIB fail: {e}")
        return []

def lrclib_get(lrc_id, timeout=15):
    url = f"{LRCLIB_BASE}/get/{lrc_id}"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': UA})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception:
        return None

# ===== Save =====

def save_lyrics(artist, album, track_name, lrc_text, plain_text):
    safe_artist = "".join(c for c in artist if c not in r'\\/:*?"<>|').strip()
    safe_album = "".join(c for c in album if c not in r'\\/:*?"<>|').strip()
    safe_track = "".join(c for c in track_name if c not in r'\\/:*?"<>|').strip()
    base = os.path.join(LYRICS_DIR, safe_artist, safe_album)
    os.makedirs(base, exist_ok=True)
    saved = []
    if lrc_text:
        path = os.path.join(base, f"{safe_track}.lrc")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(lrc_text)
        saved.append(path)
    if plain_text:
        path = os.path.join(base, f"{safe_track}.txt")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(plain_text)
        saved.append(path)
    return saved

# ===== Main Pipeline =====

def process_album(artist, album):
    print(f"\n{'='*50}")
    print(f"Album: {artist} - {album}")
    print(f"{'='*50}")
    
    # Step 1: Get tracklist from MusicBrainz
    tracks = mb_get_tracklist(artist, album)
    if not tracks:
        return None
    
    # Save tracklist
    safe_name = "".join(c for c in f"{artist}-{album}" if c not in r'\\/:*?"<>|')
    tl_path = os.path.join(TRACKLISTS_DIR, f"{safe_name}.json")
    with open(tl_path, 'w', encoding='utf-8') as f:
        json.dump({'artist': artist, 'album': album, 'tracks': tracks}, f, ensure_ascii=False, indent=2)
    
    # Step 2: Get lyrics from LRCLIB
    print(f"\n[4] LRCLIB: Get lyrics")
    ok = fail = no_lyrics = 0
    
    for t in tracks:
        title = t['title']
        print(f"  [{t['position']:2d}] {title}")
        try:
            results = lrclib_search(artist, title)
            if not results:
                print(f"      -- no results")
                no_lyrics += 1
                time.sleep(1)
                continue
            full = lrclib_get(results[0]['id'])
            if not full:
                fail += 1
                time.sleep(1)
                continue
            lrc = full.get('syncedLyrics', '')
            plain = full.get('plainLyrics', '')
            if not lrc and not plain:
                print(f"      -- no lyrics content")
                no_lyrics += 1
                time.sleep(1)
                continue
            saved = save_lyrics(artist, album, title, lrc, plain)
            print(f"      OK: {len(saved)} files")
            ok += 1
        except Exception as e:
            print(f"      ERR: {e}")
            fail += 1
        time.sleep(1)
    
    print(f"\n{'='*50}")
    print(f"Result: OK={ok} FAIL={fail} NONE={no_lyrics} TOTAL={len(tracks)}")
    print(f"{'='*50}")
    return {'ok': ok, 'fail': fail, 'no_lyrics': no_lyrics, 'total': len(tracks)}

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        artist = sys.argv[1]
        album = " ".join(sys.argv[2:])
    else:
        artist = input("Artist: ").strip()
        album = input("Album: ").strip()
    
    if not artist or not album:
        sys.exit(1)
    
    process_album(artist, album)
