"""Fix the if/else removal properly"""
js_path = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\dist\server.js'
with open(js_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the messed up block with clean code
old = """        const existing = (0, database_1.queryOne)('SELECT * FROM albums WHERE album_name = ? AND artist = ?', [album_name, artist]);
            // 创建
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

new = """        const existing = (0, database_1.queryOne)('SELECT * FROM albums WHERE album_name = ? AND artist = ?', [album_name, artist]);
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
# Also need to handle the listen_history insert: only insert if the album exists (created or already existed)
# But the line: const album = ... might return null if the INSERT didn't execute properly.
# Actually, since we're using sql.js, the INSERT is synchronous...

content = content.replace(old, new)

with open(js_path, 'w', encoding='utf-8') as f:
    f.write(content)

# Check syntax
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
