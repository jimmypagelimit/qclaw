import sqlite3
import re

def has_chinese(text):
    """Check if text contains Chinese characters."""
    if not text:
        return False
    # CJK Unified Ideographs range
    return bool(re.search(r'[\u4e00-\u9fff]', text))

conn = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
c = conn.cursor()
c.execute("SELECT album_id, album_name, artist FROM albums WHERE pitchfork_score IS NULL")
rows = c.fetchall()
conn.close()

print(f"Total albums missing PF score: {len(rows)}")
print()

# Filter Western albums
western = [(aid, aname, artist) for (aid, aname, artist) in rows 
            if not has_chinese(artist) and not has_chinese(aname)]

print(f"Western albums (likely on Pitchfork): {len(western)}")
print()
print("First 10 Western albums missing PF score:")
for aid, aname, artist in western[:10]:
    print(f"  {aid}: {artist} - {aname}")
