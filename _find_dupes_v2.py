import sqlite3, collections, re

DB_UNC = r'\\10.0.2.4\qemu\原创计划\music'
conn = sqlite3.connect(DB_UNC)
c = conn.cursor()

c.execute('SELECT album_id, album_name, artist, total_listen_count FROM albums ORDER BY artist, album_name')
rows = c.fetchall()

# 1. 大小写不敏感去重
print('=== 1. 大小写不敏感重复 ===')
seen = {}
case_dupes = []
for id_, name, artist, tc in rows:
    key = (name.lower().strip(), artist.lower().strip())
    if key in seen:
        case_dupes.append((seen[key], (id_, name, artist, tc)))
    else:
        seen[key] = (id_, name, artist, tc)

print(f'找到 {len(case_dupes)} 条大小写重复:\n')
for (id1, n1, a1, tc1), (id2, n2, a2, tc2) in case_dupes[:10]:
    print(f'  [{id1}] {a1} - {n1} (tc={tc1})')
    print(f'  [{id2}] {a2} - {n2} (tc={tc2})')
    print()

if len(case_dupes) > 10:
    print(f'  ...(共 {len(case_dupes)} 组)\n')

# 2. 同一艺人下相似专辑名（编辑距离）
print('\n=== 2. 同一艺人下相似专辑名 ===')
by_artist = collections.defaultdict(list)
for id_, name, artist, tc in rows:
    by_artist[artist.lower().strip()].append((id_, name, tc))

similar = []
for artist, albums in by_artist.items():
    if len(albums) < 2:
        continue
    for i in range(len(albums)):
        for j in range(i+1, len(albums)):
            a, b = albums[i], albums[j]
            # 简单相似度：同名不同大小写已在上一步，这里看长度差<3且包含相同词
            name_a, name_b = a[1].lower(), b[1].lower()
            if abs(len(name_a) - len(name_b)) < 3:
                # 去掉标点后比较
                aa = re.sub(r'[^\w\s]', '', name_a)
                bb = re.sub(r'[^\w\s]', '', name_b)
                if aa == bb or aa in bb or bb in aa:
                    similar.append((artist, a, b))

print(f'找到 {len(similar)} 组相似专辑名:\n')
for artist, a, b in similar[:10]:
    print(f'  {artist}:')
    print(f'    [{a[0]}] {a[1]} (tc={a[2]})')
    print(f'    [{b[0]}] {b[1]} (tc={b[2]})')
    print()

conn.close()
