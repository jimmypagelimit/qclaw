"""Final cleanup: remove the last 3 total_listen_count references"""
js_path = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\dist\server.js'
with open(js_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Line 293: just "total_listen_count," in the artists SELECT
content = content.replace(
    "\n        total_listen_count,\n        avg_rating",
    "\n        (SELECT COALESCE(SUM((SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id)), 0) FROM albums a WHERE a.artist_id = artists.artist_id) as total_listens,\n        avg_rating"
)

# Lines 350-353: remove the tlc default block
old = """            // ȷ�� total_listen_count ����Ϊ 1
            const tlcIndex = fields.indexOf('total_listen_count');
            if (!values[tlcIndex])
                values[tlcIndex] = 1;
"""
content = content.replace(old, "")

count = content.count("total_listen_count")
print(f"Remaining: {count}")
if count > 0:
    for i, line in enumerate(content.split('\n')):
        if 'total_listen_count' in line:
            print(f"  L{i+1}: {line.strip()[:150]}")

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Done")
