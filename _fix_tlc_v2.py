"""Surgical replacements - one at a time"""
js_path = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\dist\server.js'
with open(js_path, 'r', encoding='utf-8') as f:
    content = f.read()

count_before = content.count('total_listen_count')
print(f"Before: {count_before}")

# 1. SELECT query replacements (safe, no Chinese characters)
content = content.replace(
    "'SELECT COALESCE(SUM(total_listen_count), 0) as total FROM albums'",
    "'SELECT COUNT(*) as total FROM listen_history'"
)
content = content.replace(
    "('SELECT * FROM albums ORDER BY total_listen_count DESC LIMIT 1')",
    "('SELECT a.*, (SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id) as cnt FROM albums a ORDER BY cnt DESC LIMIT 1')"
)
content = content.replace(
    "('SELECT * FROM albums WHERE artist LIKE ? ORDER BY total_listen_count DESC LIMIT ?',",
    "('SELECT a.*, (SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id) as cnt FROM albums a WHERE a.artist LIKE ? ORDER BY cnt DESC LIMIT ?',"
)
content = content.replace(
    "('SELECT * FROM albums ORDER BY total_listen_count DESC LIMIT ?',",
    "('SELECT a.*, (SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id) as cnt FROM albums a ORDER BY cnt DESC LIMIT ?',"
)
content = content.replace(
    "`SELECT cover_image_url FROM albums WHERE artist = ? AND cover_image_url IS NOT NULL AND cover_image_url != '' ORDER BY total_listen_count DESC LIMIT 1`",
    "`SELECT cover_image_url FROM albums a WHERE a.artist = ? AND cover_image_url IS NOT NULL AND cover_image_url != '' ORDER BY (SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id) DESC LIMIT 1`"
)
content = content.replace(
    "'a.total_listen_count'",
    "'cnt'"
)

# 2. Artist query
content = content.replace(
    "listen: 'total_listen_count'",
    "listen: 'total_listens'"
)
content = content.replace(
    "sortCol = sortMap[sort] || 'total_listen_count'",
    "sortCol = sortMap[sort] || 'total_listens'"
)
content = content.replace(
    "name as artist, total_listen_count, avg_rating",
    "name as artist, (SELECT COALESCE(SUM((SELECT COUNT(*) FROM listen_history lh2 WHERE lh2.album_id = a2.album_id)), 0) FROM albums a2 WHERE a2.artist_id = artists.artist_id) as total_listens, avg_rating"
)

# 3. Destructure: remove total_listen_count from req.body
content = content.replace(
    "total_listen_count, release_company, cover_image_url",
    "release_company, cover_image_url"
)

# 4. Remove the if(existing) update block
# Find this exact structure by reading the bytes
old_if_block = '        if (existing) {\n            // \xe5\xb7\xb2\xe5\xad\x98\xe5\x9c\xa8\xef\xbc\x9a+1 total_listen_count\n            const newCount = existing.total_listen_count + 1;\n            (0, database_1.execute)(\'UPDATE albums SET total_listen_count = ? WHERE album_id = ?\', [newCount, existing.album_id]);\n        }'
new_if_block = '        // \xe5\xb7\xb2\xe5\xad\x98\xe5\x9c\xa8\xef\xbc\x9a\xe5\x8f\xaa\xe5\x8a\xa0\xe5\x90\xac\xe6\xad\x8c\xe8\xae\xb0\xe5\xbd\x95'

# Actually let me find the exact position and use index manipulation
idx_if = content.find('if (existing) {\n')
if idx_if >= 0:
    # Find the matching } after this block
    after_if = content[idx_if:]
    # The block ends with "        }" followed by 8 spaces and "else {"
    # Look for the pattern: \n        }\n        else {
    end_if = after_if.find('\n        }\n        else {')
    if end_if >= 0:
        end_if += len('\n        }')  # position of the closing }
        block_to_remove = after_if[:end_if+1]  # include the newline after }
        print(f"Found if block at {idx_if}, length {len(block_to_remove)}")
        content = content[:idx_if] + content[idx_if + len(block_to_remove):]
        print("Removed if (existing) block")

# 5. Remove total_listen_count from fields and values
# Fields list
content = content.replace(
    "'description', 'is_compilation', 'first_listen_date', 'total_listen_count',",
    "'description', 'is_compilation', 'first_listen_date',"
)

# Value mapping - find the exact line
idx_tlc_val = content.find("\xf3 === 'total_listen_count' ? total_listen_count :")
if idx_tlc_val >= 0:
    line_start = content.rfind('\n', 0, idx_tlc_val) + 1
    line_end = content.find('\n', idx_tlc_val)
    old_line = content[line_start:line_end]
    new_line = old_line.replace("\xf3 === 'total_listen_count' ? total_listen_count : f === 'release_company' ? release_company :", "f === 'release_company' ? release_company :")
    # Oops, the f has funky encoding. Let me use repr
    print(f"OLD VALUE LINE: {repr(old_line)}")
    content = content.replace(old_line, new_line)

# 6. Remove tlc default block
idx_tlc_check = content.find('// \xc8\xb7\xb1\xa3 total_listen_count \xc4\xac\xc8\xcf\xce\xaa 1\n')
if idx_tlc_check >= 0:
    # Remove 4 lines: comment + const tlcIndex + if + values[tlcIndex] = 1
    block_end = content.find('\n', idx_tlc_check)
    block_end = content.find('\n', block_end+1)
    block_end = content.find('\n', block_end+1)
    block_end = content.find('\n', block_end+1)
    content = content[:idx_tlc_check] + content[block_end+1:]
    print("Removed tlc default block")
else:
    # Try different encoding
    idx2 = content.find('const tlcIndex = fields.indexOf')
    if idx2 >= 0:
        # Find line start
        line_start = content.rfind('\n', 0, idx2) + 1
        # Remove 4 lines
        for _ in range(4):
            line_end = content.find('\n', line_start) + 1
            content = content[:line_start] + content[line_end:]
        print("Removed tlc default block (fallback)")

# 7. Remove the POST /api/albums/:id/listen update block
idx_listen_update = content.find("// +1 total_listen_count\n")
if idx_listen_update >= 0:
    line_end = content.find('\n', idx_listen_update)
    line_end = content.find('\n', line_end+1)
    line_end = content.find('\n', line_end+1)
    content = content[:idx_listen_update] + content[line_end+1:]
    print("Removed listen endpoint update block")

# 8. Update comments
content = content.replace(
    "д�� albums �������أ�album_name + artist���Ѵ����� +1 total_listen_count��",
    "д�� listen_history"
)
content = content.replace("albums �� +1 total_listen_count", "listen_history +1 ��¼")
content = content.replace("+1 total_listen_count", "listen_history +1")

# Final check
count_after = content.count('total_listen_count')
print(f"After: {count_after}")
if count_after > 0:
    for i, line in enumerate(content.split('\n')):
        if 'total_listen_count' in line:
            print(f"  L{i+1}: {line.strip()[:200]}")

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(content)
