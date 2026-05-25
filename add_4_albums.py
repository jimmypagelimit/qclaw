#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3, os, json, urllib.request, urllib.parse, shutil

db = r'G:\原创计划\music'
cover_dir = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\covers'

albums_to_add = [
    {'name': 'Angel in Plainclothes', 'artist': 'Angelo De Augustine', 'rym': 3.44, 'tc': 3, 'genre': 'Singer-Songwriter, Indie Folk'},
    {'name': 'tanquemante', 'artist': 'Inundaremos', 'rym': 3.74, 'tc': 4, 'genre': 'Chamber Pop, Indie Pop, Indie Rock, Chamber Folk'},
    {'name': 'Is It Gonna Happen Again?', 'artist': 'jody\u79ef\u878d', 'rym': 3.51, 'tc': 1, 'genre': 'Alternative R&B, Alt-Pop'},
    {'name': '\u8131\u8f68', 'artist': '\u8c22\u751c\u67d2', 'rym': 3.40, 'tc': 1, 'genre': 'Conscious Hip Hop'},
]

conn = sqlite3.connect(db)
c = conn.cursor()

for album in albums_to_add:
    name = album['name']
    artist = album['artist']
    rym = album['rym']
    tc = album['tc']
    genre = album['genre']
    
    print(f'=== {artist} - {name} ===')
    
    # albums
    c.execute("SELECT album_id, total_listen_count, rating FROM albums WHERE album_name=? AND artist=?", (name, artist))
    r = c.fetchone()
    if r:
        albums_id = r[0]
        print(f'  albums: id={albums_id}, tc={r[1]}, RYM={r[2]}')
        c.execute('UPDATE albums SET total_listen_count=?, rating=? WHERE album_id=?', (tc, rym, albums_id))
        print(f'  updated: tc={tc}, RYM={rym}')
    else:
        c.execute('SELECT MAX(album_id) FROM albums')
        albums_id = c.fetchone()[0] + 1
        c.execute('''INSERT INTO albums (album_id, album_name, artist, release_year, first_listen_date, total_listen_count, rating, genre)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (albums_id, name, artist, 2026, '2026-05', tc, rym, genre))
        print(f'  added albums: id={albums_id}')
    
    # albums_2026
    c.execute("SELECT album_id, total_listen_count, rating FROM albums_2026 WHERE album_name=? AND artist=?", (name, artist))
    r2 = c.fetchone()
    if r2:
        albums_2026_id = r2[0]
        print(f'  albums_2026: id={albums_2026_id}, tc={r2[1]}, RYM={r2[2]}')
        c.execute('UPDATE albums_2026 SET total_listen_count=?, rating=? WHERE album_id=?', (tc, rym, albums_2026_id))
        print(f'  updated: tc={tc}, RYM={rym}')
    else:
        c.execute('SELECT MAX(album_id) FROM albums_2026')
        albums_2026_id = c.fetchone()[0] + 1
        c.execute('''INSERT INTO albums_2026 (album_id, album_name, artist, release_year, first_listen_date, total_listen_count, rating, genre)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
            (albums_2026_id, name, artist, 2026, '2026-05', tc, rym, genre))
        print(f'  added albums_2026: id={albums_2026_id}')
    
    # Cover
    safe_artist = artist.replace(' ', '_').replace('/', '_').replace('.', '')
    safe_name = name.replace(' ', '_').replace('/', '_').replace('?', '').replace(':', '').replace('.', '')
    cover1 = os.path.join(cover_dir, f'{albums_id}-{safe_artist}-{safe_name}.jpg')
    cover2 = os.path.join(cover_dir, f'{albums_2026_id}-{safe_artist}-{safe_name}.jpg')
    
    if os.path.exists(cover1):
        print(f'  Cover exists')
        if not os.path.exists(cover2):
            shutil.copy2(cover1, cover2)
    else:
        print(f'  Downloading cover...')
        found = False
        # iTunes
        try:
            url = f'https://itunes.apple.com/search?term={urllib.parse.quote(artist + " " + name)}&entity=album&limit=1'
            data = json.loads(urllib.request.urlopen(url, timeout=10).read())
            if data['resultCount'] > 0 and 'artworkUrl100' in data['results'][0]:
                img_url = data['results'][0]['artworkUrl100'].replace('100x100bb', '600x600bb')
                img = urllib.request.urlopen(img_url, timeout=10).read()
                with open(cover1, 'wb') as f:
                    f.write(img)
                shutil.copy2(cover1, cover2)
                print(f'  iTunes: {len(img)} bytes')
                found = True
        except Exception as e:
            print(f'  iTunes failed')
        
        if not found:
            try:
                url2 = f'https://api.deezer.net/search/album?q={urllib.parse.quote(artist + " " + name)}'
                data2 = json.loads(urllib.request.urlopen(url2, timeout=10).read())
                if data2.get('data') and len(data2['data']) > 0 and 'cover_big' in data2['data'][0]:
                    img_url2 = data2['data'][0]['cover_big']
                    img2 = urllib.request.urlopen(img_url2, timeout=10).read()
                    with open(cover1, 'wb') as f:
                        f.write(img2)
                    shutil.copy2(cover1, cover2)
                    print(f'  Deezer: {len(img2)} bytes')
                    found = True
            except Exception as e:
                print(f'  Deezer failed')
        
        if not found:
            print(f'  Cover NOT found')
    print()

conn.commit()
conn.close()
print('=== Done ===')
