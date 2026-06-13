"""Phase 3: handle remaining references line-by-line"""
js_path = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\dist\server.js'
with open(js_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# === 1. Artist query (lines 282-296) ===
# Change total_listen_count to total_listens, add subquery
for i, line in enumerate(lines):
    if "listen: 'total_listen_count'" in line:
        lines[i] = line.replace("listen: 'total_listen_count'", "listen: 'total_listens'")
    if "sortCol = sortMap[sort] || 'total_listen_count'" in line:
        lines[i] = line.replace("'total_listen_count'", "'total_listens'")
    if "name as artist, total_listen_count, avg_rating" in line:
        lines[i] = line.replace(
            "name as artist, total_listen_count, avg_rating",
            "name as artist, (SELECT COALESCE(SUM((SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id)), 0) FROM albums a WHERE a.artist_id = artists.artist_id) as total_listens, avg_rating"
        )

# === 2. Remove existing-album UPDATE block ===
# Lines 332-336: if (existing) { ... }  -> keep if block but empty
new_lines = []
skip_until = -1
for i, line in enumerate(lines):
    if 331 <= i < 336 and 'total_listen_count' in line:
        # Skip these lines
        continue
    if i == 331 and 'if (existing)' in line:
        # Keep the if line but change the next statement
        new_lines.append(line)
        # Skip the next 3 lines (333-335) that have the update logic
        continue
    if 332 <= i <= 335:
        continue
    new_lines.append(line)

lines = new_lines

# === 3. Remove tlc default-1 block ===
new_lines = []
skip_count = 0
for i, line in enumerate(lines):
    if 'ȷ�� total_listen_count ����Ϊ 1' in line:
        skip_count = 4  # skip this line + next 3
        continue
    if skip_count > 0:
        skip_count -= 1
        continue
    new_lines.append(line)

lines = new_lines

# === 4. Update comments ===
for i, line in enumerate(lines):
    if '+1 total_listen_count' in line:
        lines[i] = line.replace('+1 total_listen_count', 'listen_history +1')
    if 'albums 表 +1 total_listen_count' in line:
        lines[i] = line.replace('albums 表 +1 total_listen_count', 'listen_history +1 记录')

# === 5. Fix the destructure - remove total_listen_count from req.body ===
# Pattern: const { ... total_listen_count, release_company ...
for i, line in enumerate(lines):
    # Look for the line starting with "const { album_name"
    stripped = line.strip()
    if stripped.startswith("const { album_name") and "total_listen_count" in stripped:
        lines[i] = line.replace("total_listen_count, ", "")

# === 6. Remove total_listen_count from PATCH allowed_fields (2nd occurrence) ===
for i, line in enumerate(lines):
    if "total_listen_count" in line and "release_company" in line and "style" in line:
        lines[i] = line.replace("'total_listen_count', ", "")

# Check remaining
count = 0
for i, line in enumerate(lines):
    if 'total_listen_count' in line:
        idx = line.find('total_listen_count')
        print(f"  REMAINING L{i+1}: ...{line[max(0,idx-30):idx+40].strip()}...")
        count += 1
print(f"Total remaining: {count}")

with open(js_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print("Phase 3 written")
