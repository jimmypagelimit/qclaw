import sqlite3, json

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
c = conn.cursor()

# Missing tracks: count by whether artist name contains CJK characters
c.execute("""
    SELECT t.id, t.track_name, a.artist, a.album_name
    FROM tracks t JOIN albums a ON t.album_id = a.album_id
    WHERE (t.lyrics_text_path IS NULL OR t.lyrics_text_path = '')
      AND (t.lyrics_lrc_path IS NULL OR t.lyrics_lrc_path = '')
""")
rows = c.fetchall()

import re
cjk_re = re.compile(r'[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]')
chinese = []
western = []
instrumental_keywords = ['instrumental', 'demo', 'Take ', 'rehearsal', 'rough mix', 'Jam)', 'Interlude', 'Intro', 'Outro', 'Segue', 'untitled']

for track_id, track_name, artist, album_name in rows:
    has_cjk = bool(cjk_re.search(artist)) or bool(cjk_re.search(track_name))
    if has_cjk:
        chinese.append((track_id, track_name, artist, album_name))
    else:
        western.append((track_id, track_name, artist, album_name))

# Count instrumental-looking western tracks
inst_western = [r for r in western if any(kw.lower() in r[1].lower() for kw in instrumental_keywords)]
regular_western = [r for r in western if r not in inst_western]

result = {
    'total_missing': len(rows),
    'chinese_cjk': len(chinese),
    'western_total': len(western),
    'western_instrumental_like': len(inst_western),
    'western_regular': len(regular_western),
    'lrclib_actionable': len(regular_western),  # These are the ones LRCLIB might have
}

with open(r'C:\Users\qujt\.qclaw\workspace\_lyrics_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

# Print summary
for k, v in result.items():
    print(f'{k}: {v}')

# Sample regular western
print('\nSample regular western missing:')
for r in regular_western[:15]:
    print(f'  {r[2]} | {r[3]} | {r[1]}')

conn.close()
