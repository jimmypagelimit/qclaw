"""Phase 2: remove total_listen_count from INSERT/UPDATE/artist queries"""
js_path = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\dist\server.js'
with open(js_path, 'r', encoding='utf-8') as f:
    content = f.read()

# === ARTIST query: total_listen_count -> subquery ===
# SELECT artist_id, name as artist, total_listen_count, avg_rating, image_url
content = content.replace(
    "name as artist, total_listen_count, avg_rating",
    "name as artist, (SELECT COALESCE(SUM((SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id)), 0) FROM albums a WHERE a.artist_id = artists.artist_id) as total_listens, avg_rating"
)

# === EXISTING album: remove the entire update block ===
# Remove: // 已存在：+1 total_listen_count\nconst newCount = existing.total_listen_count + 1;\n(0, database_1.execute)('UPDATE albums SET total_listen_count = ? WHERE album_id = ?', [newCount, existing.album_id]);
old_existing_block = """            // 已存在：+1 total_listen_count
            const newCount = existing.total_listen_count + 1;
            (0, database_1.execute)('UPDATE albums SET total_listen_count = ? WHERE album_id = ?', [newCount, existing.album_id]);"""
content = content.replace(old_existing_block, "")

# === INSERT: remove total_listen_count from fields, values mapping, and the default-1 logic ===
# Remove from fields list
content = content.replace(
    "'description', 'is_compilation', 'first_listen_date', 'total_listen_count',",
    "'description', 'is_compilation', 'first_listen_date',"
)
# Remove from value mapping
old_val_line = """                                f === 'total_listen_count' ? total_listen_count : f === 'release_company' ? release_company :"""
content = content.replace(
    old_val_line,
    """                                f === 'release_company' ? release_company :"""
)

# Remove the destructured total_listen_count from req.body
old_destructure = "total_listen_count, release_company, cover_image_url, duration, release_year, style, producer"
content = content.replace(
    old_destructure,
    "release_company, cover_image_url, duration, release_year, style, producer"
)

# Remove the // ȷ�� total_listen_count ����Ϊ 1 block
old_tlc_default = """            // ȷ�� total_listen_count ����Ϊ 1
            const tlcIndex = fields.indexOf('total_listen_count');
            if (!values[tlcIndex])
                values[tlcIndex] = 1;"""
content = content.replace(old_tlc_default, "")

# === PATCH: remove total_listen_count from allowed fields ===
old_patch_fields = "'description', 'is_compilation', 'first_listen_date', 'total_listen_count',"
content = content.replace(
    old_patch_fields,
    "'description', 'is_compilation', 'first_listen_date',"
)

# === LISTEN endpoint: remove the +1 total_listen_count UPDATE ===
old_listen_update = """        // +1 total_listen_count
        const newCount = album.total_listen_count + Number(count);
        (0, database_1.execute)('UPDATE albums SET total_listen_count = ? WHERE album_id = ?', [newCount, id]);"""
content = content.replace(old_listen_update, "")

# === Update comments (descriptive only) ===
content = content.replace(
    "*   1. 写入 albums 判重（album_name + artist）已存在 +1 total_listen_count",
    "*   1. 写入 listen_history"
)
content = content.replace(
    "*   1. albums 表 +1 total_listen_count",
    "*   1. listen_history 写一条记录"
)

count = content.count("total_listen_count")
print(f"Remaining total_listen_count references: {count}")

if count > 0:
    for i, line in enumerate(content.split('\n')):
        if 'total_listen_count' in line:
            idx = line.find('total_listen_count')
            print(f"  LINE {i+1}: {line[max(0,idx-40):idx+40].strip()}")

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Phase 2 complete")
