import sys, io, re, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = r'C:\Users\qujt\.qclaw\workspace\tasks\rym-expert\data\artists'

for slug in ['csh', 'sonic_youth', 'the_cure']:
    html_path = os.path.join(DATA_DIR, f'{slug}_full.html')
    with open(html_path, encoding='utf-8') as f:
        html = f.read()
    
    meta = {}
    
    # Name from meta description
    m = re.search(r'name="description"\s+content="([^"]+)"', html)
    if m:
        desc = m.group(1)
        # Parse "Artist, formed YEAR. Genres: G1, G2. Albums include A1, A2, and A3."
        print(f'\n=== {slug} ===')
        print(f'Meta desc: {desc[:300]}')
        genres_m = re.search(r'Genres?:\s*([^.]*)', desc)
        if genres_m:
            meta['genres'] = [g.strip() for g in genres_m.group(1).split(',') if g.strip()]
            print(f'Genres: {meta["genres"]}')
        
        albums_m = re.search(r'Albums?\s+include\s*(.+?)\.?$', desc)
        if albums_m:
            meta['notable_albums'] = [a.strip() for a in albums_m.group(1).replace(' and ', ',').split(',') if a.strip()]
            print(f'Notable: {meta["notable_albums"]}')
    
    # Search for "descriptive" content
    # RYM uses descriptives as tags - look for class containing "descriptive"
    desc_patterns = [
        r'class="[^"]*descriptive[^"]*"[^>]*>([^<]+)<',
        r'class="[^"]*descriptive[^"]*"[^>]*data-text="([^"]+)"',
        r'descriptive_text[^>]*>([^<]+)',
    ]
    for pat in desc_patterns:
        found = re.findall(pat, html)
        if found:
            meta['descriptives_raw'] = found[:20]
            print(f'Descriptives (pat): {[d.strip() for d in found[:15]]}')
            break
    
    # Look for "descriptive" in any form
    desc_idx = html.lower().find('descriptive')
    if desc_idx > 0:
        print(f'Descriptive found at {desc_idx}')
        print(html[desc_idx-20:desc_idx+300])
    else:
        print('No "descriptive" found in HTML')
    
    # Similar artists - look for specific section patterns
    # Check for "Fans also like" or "Similar" sections
    for kw in ['Fans also like', 'similar artists', 'Fans of', 'Related', 'Listeners also']:
        if kw.lower() in html.lower():
            idx = html.lower().find(kw.lower())
            section = html[idx:idx+1000]
            links = re.findall(r'href="/artist/([^"/]+)"[^>]*>([^<]+)<', section)
            print(f'{kw}: {[n.strip() for _, n in links[:10]]}')
    
    # Check what's in the right sidebar / page sections
    # Look for section headers
    h2s = re.findall(r'<h\d[^>]*>(.*?)</h\d>', html, re.DOTALL)
    print(f'\nAll headings:')
    for h in h2s:
        clean = re.sub(r'<[^>]+>', '', h).strip()
        if clean and len(clean) < 60:
            print(f'  {clean}')
