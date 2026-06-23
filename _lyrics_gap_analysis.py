# -*- coding: utf-8 -*-
import sqlite3, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DB_PATH = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Sample tracks without lyrics
c.execute("""SELECT t.track_name, a.artist, a.album_name, a.country
              FROM tracks t 
              LEFT JOIN albums a ON t.album_id = a.album_id
              WHERE (t.lyrics_text_path IS NULL OR t.lyrics_text_path = '') 
                AND (t.lyrics_lrc_path IS NULL OR t.lyrics_lrc_path = '')
              ORDER BY RANDOM()
              LIMIT 30""")

print("=== Random sample of tracks without lyrics ===")
for row in c.fetchall():
    print(f"  {row[1]} - {row[0]} (from {row[2]}) [{row[3]}]")

# Count by country
c.execute("""SELECT a.country, COUNT(*) as cnt
              FROM tracks t 
              LEFT JOIN albums a ON t.album_id = a.album_id
              WHERE (t.lyrics_text_path IS NULL OR t.lyrics_text_path = '') 
                AND (t.lyrics_lrc_path IS NULL OR t.lyrics_lrc_path = '')
              GROUP BY a.country
              ORDER BY cnt DESC
              LIMIT 10""")

print("\n=== Missing lyrics by country ===")
for row in c.fetchall():
    print(f"  {row[0]}: {row[1]} tracks")

# Check if these are instrumental
c.execute("""SELECT t.track_name, a.artist
              FROM tracks t 
              LEFT JOIN albums a ON t.album_id = a.album_id
              WHERE (t.lyrics_text_path IS NULL OR t.lyrics_text_path = '') 
                AND (t.lyrics_lrc_path IS NULL OR t.lyrics_lrc_path = '')
                AND (LOWER(t.track_name) LIKE '%intro%' 
                  OR LOWER(t.track_name) LIKE '%outro%'
                  OR LOWER(t.track_name) LIKE '%interlude%'
                  OR LOWER(t.track_name) LIKE '%skit%'
                  OR LOWER(t.track_name) LIKE '%instrumental%'
                  OR LOWER(t.track_name) LIKE '%ambient%'
                  OR LOWER(t.track_name) LIKE '%segue%')
              LIMIT 20""")

print("\n=== Likely instrumental tracks ===")
for row in c.fetchall():
    print(f"  {row[1]} - {row[0]}")

conn.close()
