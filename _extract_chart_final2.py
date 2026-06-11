#!/usr/bin/env python3
"""RYM Charts 最终版 - 修复 abbr 提取"""
import re, os, json

OUT = r'C:\Users\qujt\.qclaw\workspace\rym_explore'

def extract_chart_albums(html_path, label):
    with open(html_path, encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    albums = []
    pos_pattern = re.compile(r'<div id="pos(\d+)"[^>]*>(.*?)(?=<div id="pos\d+"|\Z)', re.DOTALL)
    
    for m in pos_pattern.finditer(content):
        rank = int(m.group(1))
        block = m.group(2)
        
        # Rating
        rating_m = re.search(r'class="page_charts_section_charts_item_details_average_num">(\d\.\d{2})</span>', block)
        rating = rating_m.group(1) if rating_m else ''
        if not rating:
            continue
        
        # Rating count - look in the outer stats div
        count = ''
        stats_m = re.search(r'class="page_charts_section_charts_item_stats compact">(.*?)</div>\s*</div>', block, re.DOTALL)
        if stats_m:
            abbr_m = re.search(r'class="abbr">\s*(\S+)\s*</span>', stats_m.group(1))
            count = abbr_m.group(1) if abbr_m else ''
        
        # Album title
        album_m = re.search(r'<a[^>]+class="[^"]*release[^"]*"[^>]*>.*?<span class="ui_name_locale_original">([^<]+)</span>', block, re.DOTALL)
        album_title = album_m.group(1).strip() if album_m else ''
        
        # Album URL
        album_url_m = re.search(r'<a[^>]+class="[^"]*release[^"]*"[^>]*href="([^"?#]+)"', block)
        album_url = album_url_m.group(1) if album_url_m else ''
        
        # Artist
        artist_m = re.search(r'<a[^>]+class="[^"]*artist[^"]*"[^>]*>.*?<span class="ui_name_locale_original">([^<]+)</span>', block, re.DOTALL)
        artist_name = artist_m.group(1).strip() if artist_m else ''
        
        # Artist URL
        artist_url_m = re.search(r'<a[^>]+class="[^"]*artist[^"]*"[^>]*href="([^"?#]+)"', block)
        artist_url = artist_url_m.group(1) if artist_url_m else ''
        
        # Genres
        genres = []
        genre_m = re.search(r'class="page_charts_section_charts_item_genres_primary">(.*?)</div>', block, re.DOTALL)
        if genre_m:
            genres = re.findall(r'>([^<]+)</a>', genre_m.group(1))
        
        # Date
        date_m = re.search(r'(\d{1,2}\s+\w+\s+\d{4})', block)
        date = date_m.group(1) if date_m else ''
        
        if album_title and artist_name:
            albums.append({
                'rank': rank,
                'album': album_title,
                'artist': artist_name,
                'rating': rating,
                'count': count,
                'genres': [g.strip() for g in genres[:3]],
                'date': date,
                'album_url': album_url,
                'artist_url': artist_url,
            })
    
    return albums

all_data = {}
for fname, label in [('charts_top.html', 'all_time'), ('charts_2010s.html', '2010s')]:
    path = os.path.join(OUT, fname)
    if os.path.exists(path):
        albums = extract_chart_albums(path, label)
        all_data[label] = albums
        print(f'{label}: {len(albums)} albums extracted')

with open(os.path.join(OUT, 'chart_data.json'), 'w', encoding='utf-8') as f:
    json.dump(all_data, f, indent=2, ensure_ascii=False)

# Print summary
print('\nAll-time Top 20:')
for a in all_data.get('all_time', [])[:20]:
    print(f'  #{a["rank"]:>3} {a["rating"]}/5 ({a["count"]:>5}) | {a["artist"][:22]:22} | {a["album"][:35]:35}')

print('\n2010s Top 20:')
for a in all_data.get('2010s', [])[:20]:
    print(f'  #{a["rank"]:>3} {a["rating"]}/5 ({a["count"]:>5}) | {a["artist"][:22]:22} | {a["album"][:35]:35}')

print('\nDone!')
