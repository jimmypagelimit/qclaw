"""Handle the last 3 remaining references"""
js_path = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\dist\server.js'
with open(js_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Artist SELECT (line 293)
old = "        name as artist,\n        total_listen_count,\n        avg_rating,"
new = "        name as artist,\n        (SELECT COALESCE(SUM((SELECT COUNT(*) FROM listen_history lh2 WHERE lh2.album_id = a2.album_id)), 0) FROM albums a2 WHERE a2.artist_id = artists.artist_id) as total_listens,\n        avg_rating,"
content = content.replace(old, new)

# 2. Value mapping (line 344) - use repr to get exact string
old_val = "f === 'total_listen_count' ? total_listen_count : f === 'release_company' ? release_company :"
content = content.replace(old_val, "f === 'release_company' ? release_company :")

# 3. Comment (line 349)
old_comment = "// 确保 total_listen_count 默认为 1"
content = content.replace(old_comment, "")

count = content.count('total_listen_count')
print(f"Remaining: {count}")
if count > 0:
    for i, line in enumerate(content.split('\n')):
        if 'total_listen_count' in line:
            print(f"  L{i+1}: {line.strip()[:200]}")

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Done")
