#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sqlite3, os, json, urllib.request, shutil

db = r'G:\原创计划\music'
conn = sqlite3.connect(db)
c = conn.cursor()

print('=== Aldous Harding - Train on the Island ===')

# albums
c.execute("SELECT album_id, album_name, artist, total_listen_count, rating FROM albums WHERE artist LIKE '%Aldous Harding%'")
r = c.fetchone()
if r:
    print(f'albums: id={r[0]}, name={r[1]}, tc={r[3]}, RYM={r[4]}')
    albums_id = r[0]
else:
    print('albums: Not found')
    c.execute('SELECT MAX(album_id) FROM albums')
    new_id = c.fetchone()[0] + 1
    c.execute('''INSERT INTO albums (album_id, album_name, artist, release_year, first_listen_date, total_listen_count, rating, genre, source, added_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (new_id, 'Train on the Island', 'Aldous Harding', 2026, '2026-05', 1, 3.50, 'Singer-Songwriter, Indie Folk', 'RYM', '2026-05-23'))
    conn.commit()
    print(f'Added albums id={new_id}')
    albums_id = new_id

# albums_2026
c.execute("SELECT album_id, album_name, artist, total_listen_count, rating FROM albums_2026 WHERE artist LIKE '%Aldous Harding%'")
r2 = c.fetchone()
if r2:
    print(f'albums_2026: id={r2[0]}, name={r2[1]}, tc={r2[3]}, RYM={r2[4]}')
    albums_2026_id = r2[0]
else:
    print('albums_2026: Not found')
    c.execute('SELECT MAX(album_id) FROM albums_2026')
    new_id2 = c.fetchone()[0] + 1
    c.execute('''INSERT INTO albums_2026 (album_id, album_name, artist, release_year, first_listen_date, total_listen_count, rating, genre, source, added_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (new_id2, 'Train on the Island', 'Aldous Harding', 2026, '2026-05', 1, 3.50, 'Singer-Songwriter, Indie Folk', 'RYM', '2026-05-23'))
    conn.commit()
    print(f'Added albums_2026 id={new_id2}')
    albums_2026_id = new_id2

conn.close()
print('Done')
