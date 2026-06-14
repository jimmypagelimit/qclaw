#!/usr/bin/env python3
"""
MusicBrainz 曲目表获取 - Playwright 版 v3
改进 release 选择逻辑
"""
import json, sys, os, time

def get_tracklist(artist, album):
    from playwright.sync_api import sync_playwright
    from urllib.parse import quote
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=['--no-sandbox'])
        page = browser.new_page()
        
        try:
            # Step 1: 搜索 release-group
            search_url = f"https://musicbrainz.org/search?query={quote(artist)}+{quote(album)}&type=release_group&method=indexed"
            print(f"[1] Search: {artist} - {album}")
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
            
            # Step 2: 进入 release-group 页面，找所有 release
            print(f"\n[2] Open release-group page")
            page.goto(rg_url, timeout=30000, wait_until='domcontentloaded')
            page.wait_for_timeout(3000)
            
            # 收集所有 release 链接 + 格式信息
            release_table = page.query_selector('table.tbl.mergeable-table')
            if not release_table:
                release_table = page.query_selector('table.tbl')
            
            print(f"    release_table found: {release_table is not None}")
            all_tables = page.query_selector_all('table')
            print(f"    total tables on page: {len(all_tables)}")
            
            releases = []
            if release_table:
                tbl_rows = release_table.query_selector_all('tr')
                for row in tbl_rows:
                    cells = row.query_selector_all('td')
                    if len(cells) >= 4:
                        release_link = cells[0].query_selector('a')
                        format_text = cells[2].inner_text().strip() if len(cells) > 2 else ''
                        tracks_text = cells[3].inner_text().strip() if len(cells) > 3 else ''
                        
                        if release_link:
                            href = release_link.get_attribute('href') or ''
                            # MB release-group 页面链接可能是 /release/xxx/cover-art
                            # 去掉 /cover-art 后缀
                            if href.endswith('/cover-art'):
                                href = href[:-10]
                            
                            if '/release/' in href:
                                releases.append({
                                    'href': href,
                                    'title': release_link.inner_text().strip(),
                                    'format': format_text,
                                    'tracks': tracks_text,
                                })
            
            print(f"    Found {len(releases)} releases:")
            for r in releases:
                print(f"      {r['title']} | {r['format']} | tracks={r['tracks']}")
            
            # 优先选 Digital Media
            target = None
            for r in releases:
                if 'Digital' in r['format']:
                    target = r
                    break
            if not target and releases:
                target = releases[0]
            
            if not target:
                print("    [X] No release found")
                return None
            
            print(f"    Choose: {target['title']} ({target['format']})")
            
            # Step 3: 进入 release 页面，提取曲目
            release_url = f"https://musicbrainz.org{target['href']}" if target['href'].startswith('/') else target['href']
            print(f"\n[3] Extract tracklist from {release_url}")
            page.goto(release_url, timeout=30000, wait_until='domcontentloaded')
            page.wait_for_timeout(3000)
            
            tracks = []
            # 曲目在 class='tbl medium' 表格中
            for tbl in page.query_selector_all('table.tbl.medium'):
                for row in tbl.query_selector_all('tr'):
                    cells = row.query_selector_all('td')
                    if len(cells) >= 4:
                        pos_text = cells[0].inner_text().strip()
                        title_cell = cells[1]
                        length_text = cells[3].inner_text().strip()
                        
                        try:
                            pos = int(pos_text)
                        except ValueError:
                            continue
                        
                        title_link = title_cell.query_selector('a')
                        title = title_link.inner_text().strip() if title_link else title_cell.inner_text().strip().split('\n')[0].strip()
                        
                        dur_ms = 0
                        if ':' in length_text:
                            parts = length_text.split(':')
                            try:
                                dur_ms = (int(parts[0]) * 60 + int(parts[1])) * 1000
                            except ValueError:
                                pass
                        
                        tracks.append({'position': pos, 'title': title, 'duration_ms': dur_ms})
            
            # 如果上面没找到，试另一种表格结构
            if not tracks:
                for tbl in page.query_selector_all('table.tbl'):
                    for row in tbl.query_selector_all('tr'):
                        cells = row.query_selector_all('td')
                        if len(cells) >= 3:
                            pos_text = cells[0].inner_text().strip()
                            if not pos_text.isdigit():
                                continue
                            title = cells[1].inner_text().strip().split('\n')[0].strip()
                            length_text = cells[2].inner_text().strip() if len(cells) > 2 else ''
                            dur_ms = 0
                            if ':' in length_text:
                                parts = length_text.split(':')
                                try:
                                    dur_ms = (int(parts[0]) * 60 + int(parts[1])) * 1000
                                except ValueError:
                                    pass
                            tracks.append({'position': int(pos_text), 'title': title, 'duration_ms': dur_ms})
            
            print(f"    {len(tracks)} tracks:")
            for t in tracks:
                dur = f"{t['duration_ms']//1000}s" if t['duration_ms'] else "?"
                print(f"      {t['position']:2d}. {t['title']} ({dur})")
            
            return tracks
            
        finally:
            browser.close()

def save_tracklist(artist, album, tracks):
    out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tracklists")
    os.makedirs(out_dir, exist_ok=True)
    safe_name = "".join(c for c in f"{artist}-{album}" if c not in r'\\/:*?"<>|')
    out_path = os.path.join(out_dir, f"{safe_name}.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({'artist': artist, 'album': album, 'tracks': tracks}, f, ensure_ascii=False, indent=2)
    print(f"\nSaved: {out_path}")
    return out_path

if __name__ == '__main__':
    if len(sys.argv) >= 3:
        artist = sys.argv[1]
        album = " ".join(sys.argv[2:])
    else:
        artist = input("Artist: ").strip()
        album = input("Album: ").strip()
    
    tracks = get_tracklist(artist, album)
    if tracks:
        save_tracklist(artist, album, tracks)
