import sqlite3
import re
import json

def has_chinese(text):
    """Check if text contains Chinese characters."""
    if not text:
        return False
    return bool(re.search(r'[\u4e00-\u9fff]', text))

conn = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
c = conn.cursor()

# Get all albums missing PF score
c.execute("SELECT album_id, album_name, artist FROM albums WHERE pitchfork_score IS NULL")
rows = c.fetchall()
conn.close()

# Filter Western albums
western = []
for aid, aname, artist in rows:
    if not has_chinese(artist) and not has_chinese(aname):
        western.append({'id': aid, 'artist': artist, 'album': aname})

print(f"Total missing PF: {len(rows)}")
print(f"Western albums: {len(western)}")
print(f"Chinese albums (skip): {len(rows) - len(western)}")
print()
print("First 20 Western albums:")
for item in western[:20]:
    print(f"  {item['id']}: {item['artist']} - {item['album']}")

# Save to file for batch processing
with open(r'C:\Users\qujt\.qclaw\workspace\pf_western_albums.json', 'w', encoding='utf-8') as f:
    json.dump(western, f, ensure_ascii=False, indent=2)

print(f"\nSaved to: pf_western_albums.json")
print(f"Total Western albums to process: {len(western)}")
