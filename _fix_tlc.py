"""Replace total_listen_count in server.js with listen_history COUNT subqueries"""
import re

js_path = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\dist\server.js'
with open(js_path, 'r', encoding='utf-8') as f:
    content = f.read()

original = content

# 1. Stats - SUM total -> COUNT from listen_history
content = content.replace(
    "'SELECT COALESCE(SUM(total_listen_count), 0) as total FROM albums'",
    "'SELECT COUNT(*) as total FROM listen_history'"
)

# 2. Top album - ORDER BY total_listen_count -> subquery
content = content.replace(
    "('SELECT * FROM albums ORDER BY total_listen_count DESC LIMIT 1')",
    "('SELECT a.*, (SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id) as cnt FROM albums a ORDER BY cnt DESC LIMIT 1')"
)

# 3. Artist search - ORDER BY
# The artist search query was: 'SELECT * FROM albums WHERE artist LIKE ? ORDER BY total_listen_count DESC LIMIT ?'
# We only want to replace this specific one that has WHERE artist LIKE
content = content.replace(
    "('SELECT * FROM albums WHERE artist LIKE ? ORDER BY total_listen_count DESC LIMIT ?',",
    "('SELECT a.*, (SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id) as cnt FROM albums a WHERE a.artist LIKE ? ORDER BY cnt DESC LIMIT ?',"
)

# 4. Album list - ORDER BY (without WHERE)
content = content.replace(
    "('SELECT * FROM albums ORDER BY total_listen_count DESC LIMIT ?',",
    "('SELECT a.*, (SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id) as cnt FROM albums a ORDER BY cnt DESC LIMIT ?',"
)

# 5. Sort map for albums - change a.total_listen_count to cnt subquery
content = content.replace(
    "'a.total_listen_count'",
    "'cnt'"
)

# 6. Cover query for artist - ORDER BY total_listen_count
content = content.replace(
    "ORDER BY total_listen_count DESC LIMIT 1`",
    "ORDER BY (SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id) DESC LIMIT 1`"
)
# But the above also needs to alias the table... let me check the actual context
# Line 304: SELECT cover_image_url FROM albums WHERE artist = ? AND ... ORDER BY total_listen_count DESC LIMIT 1
# For this one, since we're only selecting cover_image_url, the ORDER BY is just for picking the most-listened album
# We can use a subquery without needing to alias
content = content.replace(
    "('SELECT cover_image_url FROM albums WHERE artist = ? AND cover_image_url IS NOT NULL AND cover_image_url != '' ORDER BY total_listen_count DESC LIMIT 1`,",
    "('SELECT cover_image_url FROM albums a WHERE a.artist = ? AND cover_image_url IS NOT NULL AND cover_image_url != '' ORDER BY (SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id) DESC LIMIT 1`,"
)

# Wait, the line 304 is actually a template literal using backticks, not single quotes.
# Let me check the actual format more carefully...

# Actually, looking at the original output more carefully:
# Line 304: const coverRow = (0, database_1.queryOne)(`SELECT cover_image_url FROM albums WHERE artist = ? AND cover_image_url IS NOT NULL AND cover_image_url != '' ORDER BY total_listen_count DESC LIMIT 1`, [ar.artist]);

# So it uses backtick template literals. Let me search for this specific pattern.
# Hmm, but the replacement above might be wrong since it uses single quotes.
# Let me revert and handle it differently.

count = content.count("total_listen_count")
print(f"Remaining total_listen_count references: {count}")

if count > 0:
    # Show remaining
    for i, line in enumerate(content.split('\n')):
        if 'total_listen_count' in line:
            print(f"  REMAINING: {line.strip()[:200]}")

if original != content:
    with open(js_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Written changes to server.js")
else:
    print("NO CHANGES MADE - patterns didn't match")
