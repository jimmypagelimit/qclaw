import sqlite3
DB = r"C:\Users\qujt\.qclaw\workspace\_music_latest.db"
db = sqlite3.connect(DB)
db.row_factory = sqlite3.Row

total = db.execute("SELECT COUNT(*) as n FROM tracks").fetchone()['n']
with_lrc = db.execute("SELECT COUNT(*) as n FROM tracks WHERE lyrics_lrc_path IS NOT NULL").fetchone()['n']
with_txt = db.execute("SELECT COUNT(*) as n FROM tracks WHERE lyrics_text_path IS NOT NULL").fetchone()['n']
with_any = db.execute("SELECT COUNT(*) as n FROM tracks WHERE lyrics_lrc_path IS NOT NULL OR lyrics_text_path IS NOT NULL").fetchone()['n']
missing = db.execute("SELECT COUNT(*) as n FROM tracks WHERE lyrics_lrc_path IS NULL AND lyrics_text_path IS NULL").fetchone()['n']

print(f"Total tracks: {total}")
print(f"With LRC: {with_lrc} ({100*with_lrc/total:.1f}%)")
print(f"With TXT: {with_txt} ({100*with_txt/total:.1f}%)")
print(f"With any lyrics: {with_any} ({100*with_any/total:.1f}%)")
print(f"Missing lyrics: {missing} ({100*missing/total:.1f}%)")
db.close()
