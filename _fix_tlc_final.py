"""Clean replacement of all total_listen_count in server.js"""
import re

js_path = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\dist\server.js'
with open(js_path, 'r', encoding='utf-8') as f:
    content = f.read()

count_before = content.count('total_listen_count')
print(f"Before: {count_before} references")

# 1. Stats: SUM(total_listen_count) -> COUNT(*) from listen_history
content = content.replace(
    "'SELECT COALESCE(SUM(total_listen_count), 0) as total FROM albums'",
    "'SELECT COUNT(*) as total FROM listen_history'"
)

# 2. Top album: ORDER BY total_listen_count -> subquery
content = content.replace(
    "('SELECT * FROM albums ORDER BY total_listen_count DESC LIMIT 1')",
    "('SELECT a.*, (SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id) as cnt FROM albums a ORDER BY cnt DESC LIMIT 1')"
)

# 3. Artist search sort
content = content.replace(
    "('SELECT * FROM albums WHERE artist LIKE ? ORDER BY total_listen_count DESC LIMIT ?',",
    "('SELECT a.*, (SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id) as cnt FROM albums a WHERE a.artist LIKE ? ORDER BY cnt DESC LIMIT ?',"
)

# 4. Album list sort (no WHERE)
content = content.replace(
    "('SELECT * FROM albums ORDER BY total_listen_count DESC LIMIT ?',",
    "('SELECT a.*, (SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id) as cnt FROM albums a ORDER BY cnt DESC LIMIT ?',"
)

# 5. Sort map: 'a.total_listen_count' -> 'cnt'
content = content.replace(
    "'a.total_listen_count'",
    "'cnt'"
)

# 6. Cover query for artist fallback
content = content.replace(
    "`SELECT cover_image_url FROM albums WHERE artist = ? AND cover_image_url IS NOT NULL AND cover_image_url != '' ORDER BY total_listen_count DESC LIMIT 1`",
    "`SELECT cover_image_url FROM albums a WHERE a.artist = ? AND cover_image_url IS NOT NULL AND cover_image_url != '' ORDER BY (SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id) DESC LIMIT 1`"
)

# 7. Artist sort map: 'listen' -> 'total_listens'
content = content.replace(
    "listen: 'total_listen_count'",
    "listen: 'total_listens'"
)

# 8. Artist sort fallback
content = content.replace(
    "sortCol = sortMap[sort] || 'total_listen_count'",
    "sortCol = sortMap[sort] || 'total_listens'"
)

# 9. Artist SELECT column
content = content.replace(
    "name as artist, total_listen_count, avg_rating",
    "name as artist, (SELECT COALESCE(SUM((SELECT COUNT(*) FROM listen_history lh2 WHERE lh2.album_id = a2.album_id)), 0) FROM albums a2 WHERE a2.artist_id = artists.artist_id) as total_listens, avg_rating"
)

# 10. POST /api/albums: remove existing-album UPDATE block
# Pattern: if (existing) { ... update total_listen_count ... } else { ... insert ...
# Replace with: if (!existing) { ... insert ... }
old_post_block = """        const existing = (0, database_1.queryOne)('SELECT * FROM albums WHERE album_name = ? AND artist = ?', [album_name, artist]);
        if (existing) {
            // 已存在：+1 total_listen_count
            const newCount = existing.total_listen_count + 1;
            (0, database_1.execute)('UPDATE albums SET total_listen_count = ? WHERE album_id = ?', [newCount, existing.album_id]);
        }
        else {
            // 创建
            const fields = [
                'album_name', 'artist', 'country', 'region', 'genre', 'rating',
                'description', 'is_compilation', 'first_listen_date', 'total_listen_count',
                'release_company', 'cover_image_url', 'duration', 'release_year', 'style', 'producer'
            ];
            const values = fields.map(f => {
                const val = (f === 'album_name' ? album_name : f === 'artist' ? artist :
                    f === 'country' ? country : f === 'region' ? region : f === 'genre' ? genre :
                        f === 'rating' ? rating : f === 'description' ? description :
                            f === 'is_compilation' ? is_compilation : f === 'first_listen_date' ? first_listen_date :
                                f === 'total_listen_count' ? total_listen_count : f === 'release_company' ? release_company :
                                    f === 'cover_image_url' ? cover_image_url : f === 'duration' ? duration :
                                        f === 'release_year' ? release_year : f === 'style' ? style : f === 'producer' ? producer : null) ?? null;
                return val;
            });
            // 确保 total_listen_count 默认为 1
            const tlcIndex = fields.indexOf('total_listen_count');
            if (!values[tlcIndex])
                values[tlcIndex] = 1;
            // 确保 first_listen_date 有值
            const fldIndex = fields.indexOf('first_listen_date');
            if (!values[fldIndex])
                values[fldIndex] = new Date().toISOString().split('T')[0];
            (0, database_1.execute)(`INSERT INTO albums (${fields.join(', ')}) VALUES (${fields.map(() => '?').join(', ')})`, values);
        }"""

new_post_block = """        const existing = (0, database_1.queryOne)('SELECT * FROM albums WHERE album_name = ? AND artist = ?', [album_name, artist]);
        if (!existing) {
            // 创建（不存在才插入）
            const fields = [
                'album_name', 'artist', 'country', 'region', 'genre', 'rating',
                'description', 'is_compilation', 'first_listen_date',
                'release_company', 'cover_image_url', 'duration', 'release_year', 'style', 'producer'
            ];
            const values = fields.map(f => {
                const val = (f === 'album_name' ? album_name : f === 'artist' ? artist :
                    f === 'country' ? country : f === 'region' ? region : f === 'genre' ? genre :
                        f === 'rating' ? rating : f === 'description' ? description :
                            f === 'is_compilation' ? is_compilation : f === 'first_listen_date' ? first_listen_date :
                                f === 'release_company' ? release_company :
                                    f === 'cover_image_url' ? cover_image_url : f === 'duration' ? duration :
                                        f === 'release_year' ? release_year : f === 'style' ? style : f === 'producer' ? producer : null) ?? null;
                return val;
            });
            // 确保 first_listen_date 有值
            const fldIndex = fields.indexOf('first_listen_date');
            if (!values[fldIndex])
                values[fldIndex] = new Date().toISOString().split('T')[0];
            (0, database_1.execute)(`INSERT INTO albums (${fields.join(', ')}) VALUES (${fields.map(() => '?').join(', ')})`, values);
        }"""

count1 = content.count(old_post_block)
print(f"old_post_block matches: {count1}")
content = content.replace(old_post_block, new_post_block)

# 11. PATCH /api/albums/:id allowed fields - remove total_listen_count
old_patch = "'description', 'is_compilation', 'first_listen_date', 'total_listen_count',"
content = content.replace(old_patch, "'description', 'is_compilation', 'first_listen_date',")

# 12. Destructure in POST body - remove total_listen_count
old_destruct = "total_listen_count, release_company, cover_image_url, duration, release_year, style, producer"
content = content.replace(old_destruct, "release_company, cover_image_url, duration, release_year, style, producer")

# 13. POST /api/albums/:id/listen - remove the +1 total_listen_count UPDATE block
old_listen = """        // +1 total_listen_count
        const newCount = album.total_listen_count + Number(count);
        (0, database_1.execute)('UPDATE albums SET total_listen_count = ? WHERE album_id = ?', [newCount, id]);"""
content = content.replace(old_listen, "")

# 14. Update comments
content = content.replace(
    "*   1. 写入 albums 判重（album_name + artist）已存在 +1 total_listen_count",
    "*   1. 写入 listen_history"
)
content = content.replace(
    "*   1. albums 表 +1 total_listen_count",
    "*   1. listen_history 写一条记录"
)
content = content.replace("// 已存在：+1 total_listen_count", "// 已存在：只加听歌记录")

# Final check
count_after = content.count('total_listen_count')
print(f"After: {count_after} references")
if count_after > 0:
    for i, line in enumerate(content.split('\n')):
        if 'total_listen_count' in line:
            print(f"  L{i+1}: {line.strip()[:200]}")

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(content)
print("Written")

# Syntax check
import subprocess, time
p = subprocess.Popen(['node', '-e', 'require("./dist/server.js")'],
    cwd=r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker',
    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
time.sleep(3)
err = p.stderr.read(2000).decode('utf-8', errors='replace')
if err:
    print('SYNTAX ERROR:', err[:400])
else:
    print('Syntax OK')
p.kill()
