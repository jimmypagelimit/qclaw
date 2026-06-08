"""
Re-create album_genres and album_styles intermediate tables from text fields.
Clean up dirty data in genres/styles tables.
Then copy the updated database back to remote path.
"""
import sqlite3, shutil, os, re

REMOTE_PATH = r'\\10.0.2.4\qemu\原创计划\music'
LOCAL_PATH = r'C:\Users\qujt\.qclaw\_music_sync.db'

# Step 1: Copy remote DB to local
print("[1/5] Copying remote DB to local...")
shutil.copy2(REMOTE_PATH, LOCAL_PATH)
print("  Size: %d bytes" % os.path.getsize(LOCAL_PATH))

conn = sqlite3.connect(LOCAL_PATH)
cur = conn.cursor()

# Step 2: Check current state
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [r[0] for r in cur.fetchall()]
print("\n[2/5] Current tables: %s" % tables)

# Drop old intermediate tables if exist
for t in ['album_genres', 'album_styles']:
    if t in tables:
        conn.execute("DROP TABLE %s" % t)
        print("  Dropped old %s" % t)

# Step 3: Clean and rebuild genres/styles lookup tables
print("\n[3/5] Rebuilding genres and styles tables...")

# Clear existing data
conn.execute("DELETE FROM genres")
conn.execute("DELETE FROM styles")
conn.execute("DELETE FROM sqlite_sequence WHERE name='genres'")
conn.execute("DELETE FROM sqlite_sequence WHERE name='styles'")

genre_map = {}  # genre_name -> genre_id
style_map = {}  # style_name -> style_id

def clean_split(text):
    """Split genre/style text by comma/semicolon, clean each part."""
    if not text or not text.strip():
        return []
    parts = re.split(r'[,;，；/]', text)
    result = []
    for p in parts:
        p = p.strip()
        # Skip empty, skip multi-word combos (dirty data like "Pop, Rock")
        if p and len(p.split(',')) == 1:
            result.append(p)
    return result

# Get all albums
cur.execute("SELECT album_id, genre, style FROM albums")
rows = cur.fetchall()

album_genres = []
album_styles = []

for album_id, genre_text, style_text in rows:
    # Parse genre
    genres = clean_split(genre_text)
    for order, g in enumerate(genres):
        if g not in genre_map:
            cur.execute("INSERT INTO genres (name) VALUES (?)", (g,))
            genre_map[g] = cur.lastrowid
        album_genres.append((album_id, genre_map[g], order + 1))
    
    # Parse style
    styles = clean_split(style_text)
    for order, s in enumerate(styles):
        if s not in style_map:
            cur.execute("INSERT INTO styles (name) VALUES (?)", (s,))
            style_map[s] = cur.lastrowid
        album_styles.append((album_id, style_map[s], order + 1))

conn.commit()
print("  Unique genres: %d" % len(genre_map))
print("  Unique styles: %d" % len(style_map))
print("  album_genres records: %d" % len(album_genres))
print("  album_styles records: %d" % len(album_styles))

# Step 4: Create intermediate tables and insert data
print("\n[4/5] Creating intermediate tables...")

conn.execute("""CREATE TABLE album_genres (
    album_id INTEGER NOT NULL,
    genre_id INTEGER NOT NULL,
    genre_order INTEGER DEFAULT 1,
    PRIMARY KEY (album_id, genre_id),
    FOREIGN KEY (album_id) REFERENCES albums(album_id),
    FOREIGN KEY (genre_id) REFERENCES genres(genre_id)
)""")

conn.execute("""CREATE TABLE album_styles (
    album_id INTEGER NOT NULL,
    style_id INTEGER NOT NULL,
    style_order INTEGER DEFAULT 1,
    PRIMARY KEY (album_id, style_id),
    FOREIGN KEY (album_id) REFERENCES albums(album_id),
    FOREIGN KEY (style_id) REFERENCES styles(style_id)
)""")

conn.executemany("INSERT INTO album_genres (album_id, genre_id, genre_order) VALUES (?, ?, ?)", album_genres)
conn.executemany("INSERT INTO album_styles (album_id, style_id, style_order) VALUES (?, ?, ?)", album_styles)
conn.commit()

# Verify
cur.execute("SELECT COUNT(*) FROM album_genres")
ag_count = cur.fetchone()[0]
cur.execute("SELECT COUNT(*) FROM album_styles")
as_count = cur.fetchone()[0]
print("  album_genres: %d rows" % ag_count)
print("  album_styles: %d rows" % as_count)

# Step 5: Export SQL + copy to remote
print("\n[5/5] Exporting and syncing...")

# Export database.sql
sql_path = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\database.sql'
with open(sql_path, 'w', encoding='utf-8') as f:
    for line in conn.iterdump():
        f.write(line + '\n')
print("  database.sql exported")

# Copy DB to remote
shutil.copy2(LOCAL_PATH, REMOTE_PATH)
print("  Copied to remote! Size: %d bytes" % os.path.getsize(REMOTE_PATH))

conn.close()
os.remove(LOCAL_PATH)

# Final verify
conn2 = sqlite3.connect(REMOTE_PATH)
cur2 = conn2.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables2 = [r[0] for r in cur2.fetchall()]
print("\nFinal remote tables: %s" % tables2)
cur2 = conn2.execute('SELECT COUNT(*) FROM albums')
print("albums: %d" % cur2.fetchone()[0])
for t in ['album_genres', 'album_styles', 'genres', 'styles']:
    if t in tables2:
        cur2 = conn2.execute('SELECT COUNT(*) FROM [%s]' % t)
        print("  %s: %d rows" % (t, cur2.fetchone()[0]))
conn2.close()

print("\n=== DONE! ===")
