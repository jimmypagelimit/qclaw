import sqlite3, os, json

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
c = conn.cursor()

# Check current lyrics coverage
c.execute("SELECT COUNT(*) FROM tracks")
total = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM tracks WHERE lyrics_text_path IS NOT NULL OR lyrics_lrc_path IS NOT NULL")
with_lyrics = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM tracks WHERE lyrics_lrc_path IS NOT NULL")
with_lrc = c.fetchone()[0]

print('Total tracks:', total)
print('With any lyrics:', with_lyrics, f'({with_lyrics*100/total:.1f}%)')
print('With LRC:', with_lrc, f'({with_lrc*100/total:.1f}%)')
print('Missing:', total - with_lyrics, f'({(total-with_lyrics)*100/total:.1f}%)')

# Check batch state if exists
batch_state = r'C:\Users\qujt\.qclaw\workspace\_lyrics_batch_state.txt'
if os.path.exists(batch_state):
    with open(batch_state) as f:
        print('\nBatch state:', f.read()[:500])

# Check latest status JSON
status_file = r'C:\Users\qujt\.qclaw\workspace\_lyrics_status.json'
if os.path.exists(status_file):
    with open(status_file) as f:
        try:
            data = json.load(f)
            print('\nStatus JSON keys:', list(data.keys()))
            if 'last_run' in data:
                print('Last run:', data.get('last_run'))
            if 'progress' in data:
                print('Progress:', data.get('progress'))
        except:
            pass

conn.close()
