import sys, io, re, json, os, time
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = r'C:\Users\qujt\.qclaw\workspace\tasks\rym-expert\data\artists'

def extract_discography(html):
    releases = []
    pattern = re.compile(
        r'disco_release"[^>]*>.*?'
        r'disco_avg_rating[^">]*"[^>]*>([\d.]+)<.*?'
        r'disco_ratings[^>]*>([\d,]+)<.*?'
        r'disco_reviews[^>]*>([\d,]+)<.*?'
        r'<a class="album"[^>]*href="(/release/[^"]+)"[^>]*>([^<]+)<.*?'
        r'disco_year_ymd"[^>]*>(\d{4})<',
        re.DOTALL
    )
    for m in pattern.finditer(html):
        releases.append({
            'rating': float(m.group(1)),
            'ratings': m.group(2).replace(',', ''),
            'reviews': m.group(3).replace(',', ''),
            'url': 'https://rateyourmusic.com' + m.group(4),
            'title': m.group(5).strip(),
            'year': int(m.group(6)),
        })
    releases.sort(key=lambda x: (-x['rating'], -int(x['ratings'])))
    return releases

def extract_related(html, current_slug):
    # Find "Related" section
    idx = html.lower().find('related')
    if idx < 0:
        return []
    section = html[idx:idx+2000]
    links = re.findall(r'href="/artist/([^"/]+)"[^>]*>([^<]+)<', section)
    return [{'name': n.strip(), 'slug': s} for s, n in links if s != current_slug and '/credits' not in s and '/lists' not in s][:20]

def extract_biography(html):
    # Find Biography section
    idx = html.find('Biography')
    if idx < 0:
        return ''
    bio_start = html.find('</h', idx)
    if bio_start < 0:
        return ''
    bio_end = html.find('</div>', bio_start + 100)
    if bio_end < 0:
        bio_end = min(bio_start + 2000, len(html))
    bio_html = html[bio_start:bio_end]
    bio = re.sub(r'<[^>]+>', ' ', bio_html).strip()
    bio = re.sub(r'\s+', ' ', bio)
    return bio[:500]

def process(slug):
    html_path = os.path.join(DATA_DIR, f'{slug}_full.html')
    with open(html_path, encoding='utf-8') as f:
        html = f.read()
    
    # Meta description
    m = re.search(r'name="description"\s+content="([^"]+)"', html)
    meta_desc = m.group(1) if m else ''
    
    # Artist name
    m = re.search(r'class="artist_name_hdr"[^>]*>([^<]+)', html)
    name = m.group(1).strip() if m else slug
    
    # Formation year
    m = re.search(r'formed\s+(\d{4}|January\s+\d{4})', meta_desc)
    formed = m.group(1).strip() if m else ''
    
    # Genres from meta
    genres_m = re.search(r'Genres?:\s*([^.]*)', meta_desc)
    genres = [g.strip() for g in genres_m.group(1).split(',') if g.strip()] if genres_m else []
    
    # Notable albums
    albums_m = re.search(r'Albums?\s+include\s*(.+?)\.?$', meta_desc)
    notable = [a.strip() for a in albums_m.group(1).replace(' and ', ',').split(',') if a.strip()] if albums_m else []
    
    # Related artists
    related = extract_related(html, slug.replace('_', '-'))
    
    # Biography
    bio = extract_biography(html)
    
    # Discography
    discog = extract_discography(html)
    
    # Stats
    lists_m = re.search(r'(\d[\d,]*)\s+Lists', html)
    lists_count = lists_m.group(1).replace(',', '') if lists_m else ''
    
    output = {
        'name': name,
        'slug': slug,
        'extracted': time.strftime('%Y-%m-%d %H:%M'),
        'formed': formed,
        'genres': genres,
        'notable_albums': notable,
        'related_artists': related,
        'biography': bio[:500] if bio else None,
        'lists_count': lists_count,
        'discography': discog,
        'total_releases': len(discog),
        'top_5': discog[:5],
    }
    
    json_path = os.path.join(DATA_DIR, f'{slug}_discog.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    return output

for slug in ['csh', 'sonic_youth', 'the_cure']:
    data = process(slug)
    print(f'{data["name"]}: {data["total_releases"]} releases, {len(data["related_artists"])} related')
    print(f'  Genres: {", ".join(data["genres"])}')
    print(f'  Formed: {data["formed"]}')
    print(f'  Related: {", ".join([a["name"] for a in data["related_artists"][:8]])}')
    if data["biography"]:
        print(f'  Bio: {data["biography"][:150]}...')
    print()

# Summary
summary = {
    'date': time.strftime('%Y-%m-%d'),
    'description': 'RYM Artist Discography + Metadata (v3, JS location.href)',
    'artists': ['Car Seat Headrest', 'Sonic Youth', 'The Cure'],
    'method': 'CloakBrowser + JS location.href + regex extraction',
    'data_dir': DATA_DIR,
}
with open(os.path.join(DATA_DIR, '_summary.json'), 'w', encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print('All done.')
