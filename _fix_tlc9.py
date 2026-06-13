"""Fix: find end marker correctly"""
js_path = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\dist\server.js'
with open(js_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = None
end_idx = None
for i, line in enumerate(lines):
    if "const existing = (0, database_1.queryOne)(" in line:
        start_idx = i
    if start_idx is not None and 'execute)(' in line and 'INSERT INTO albums' in line:
        end_idx = i + 1
        break

print(f"start={start_idx}, end={end_idx}")
if start_idx is None or end_idx is None:
    print("Could not find markers!")
    # Debug: find exact matches
    for i, line in enumerate(lines):
        if 'existing' in line and 'queryOne' in line:
            print(f"  L{i+1}: {repr(line[:80])}")
        if 'INSERT INTO albums' in line:
            print(f"  L{i+1}: {repr(line[:80])}")
else:
    indent = "        "
    inner = "            "
    replacement = [
        f'{indent}const existing = (0, database_1.queryOne)(\'SELECT * FROM albums WHERE album_name = ? AND artist = ?\', [album_name, artist]);\n',
        f'{indent}if (!existing) {{\n',
        f'{inner}// 创建（不存在才插入）\n',
        f'{inner}const fields = [\n',
        f"{inner}    'album_name', 'artist', 'country', 'region', 'genre', 'rating',\n",
        f"{inner}    'description', 'is_compilation', 'first_listen_date',\n",
        f"{inner}    'release_company', 'cover_image_url', 'duration', 'release_year', 'style', 'producer'\n",
        f'{inner}];\n',
        f'{inner}const values = fields.map(f => {{\n',
        f"{inner}    const val = (f === 'album_name' ? album_name : f === 'artist' ? artist :\n",
        f"{inner}        f === 'country' ? country : f === 'region' ? region : f === 'genre' ? genre :\n",
        f"{inner}            f === 'rating' ? rating : f === 'description' ? description :\n",
        f"{inner}                f === 'is_compilation' ? is_compilation : f === 'first_listen_date' ? first_listen_date :\n",
        f"{inner}                    f === 'release_company' ? release_company :\n",
        f"{inner}                        f === 'cover_image_url' ? cover_image_url : f === 'duration' ? duration :\n",
        f"{inner}                            f === 'release_year' ? release_year : f === 'style' ? style : f === 'producer' ? producer : null) ?? null;\n",
        f'{inner}    return val;\n',
        f'{inner}}});\n',
        f'{inner}// 确保 first_listen_date 有值\n',
        f"{inner}const fldIndex = fields.indexOf('first_listen_date');\n",
        f'{inner}if (!values[fldIndex])\n',
        f'{inner}    values[fldIndex] = new Date().toISOString().split(\'T\')[0];\n',
        f"{inner}(0, database_1.execute)(`INSERT INTO albums (${{fields.join(', ')}}) VALUES (${{fields.map(() => '?').join(', ')}})`, values);\n",
        f'{indent}}}\n',
    ]

    lines = lines[:start_idx] + replacement + lines[end_idx:]

    with open(js_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
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
