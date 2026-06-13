"""Fix false positive PF scores + find correct CSH album IDs"""
import sqlite3, json
DB_PATH = r"C:\Users\qujt\.qclaw\workspace\_music_latest.db"
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row

# 1. Clear known false positives
false_pos = [3, 4, 5, 348]
print("Clearing false positives:")
for aid in false_pos:
    r = conn.execute("SELECT album_name, artist FROM albums WHERE album_id = ?", (aid,)).fetchone()
    print(f"  album_id={aid}: {repr(r['artist'])} — {repr(r['album_name'])}")
    conn.execute("UPDATE albums SET pitchfork_score = NULL, review_url = NULL WHERE album_id = ?", (aid,))

# 2. Find actual CSH albums
print("\nCSH albums in DB:")
csh = conn.execute("SELECT album_id, album_name, artist, release_year FROM albums WHERE LOWER(artist) LIKE '%car%seat%headrest%'").fetchall()
for r in csh:
    print(f"  album_id={r['album_id']}: {r['album_name']} ({r['release_year']})")

# Set correct scores
print("\nSetting correct CSH scores...")
# Twin Fantasy (Mirror to Mirror) - probably album_id=1 or similar
tf_rows = conn.execute("SELECT album_id, album_name, release_year FROM albums WHERE album_name LIKE '%Twin Fantasy%'").fetchall()
for r in tf_rows:
    print(f"  Twin Fantasy candidate: album_id={r['album_id']}: {r['album_name']} ({r['release_year']})")

# Teens of Denial
tod_rows = conn.execute("SELECT album_id, album_name, release_year FROM albums WHERE album_name LIKE '%Teens of Denial%'").fetchall()
for r in tod_rows:
    print(f"  Teens of Denial candidate: album_id={r['album_id']}: {r['album_name']} ({r['release_year']})")

conn.commit()
conn.close()
