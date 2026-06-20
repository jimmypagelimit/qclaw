import sqlite3

db = 'C:/Users/qujt/.qclaw/workspace/_music_latest.db'
conn = sqlite3.connect(db)
c = conn.cursor()

c.execute("""SELECT album_id, album_name, artist
    FROM albums
    WHERE release_mbid IS NULL OR release_mbid = ''
    ORDER BY artist, album_name
""")

rows = c.fetchall()
conn.close()

# 分类
categories = {
    '华语主流（有希望）': [],
    '华语独立（难）': [],
    '外语独立（难）': [],
    '合辑/Various Artists': [],
    '翻唱/现场（难）': [],
}

mainstream_artists = ['罗大佑', '张雨生', '张悬', '吴青峰', '林忆莲', '王杰', '陈绮贞', '魏如萱', '周华健', '郑智化', '高枫', '许景淳', '达明一派']

for r in rows:
    aid, aname, artist = r
    key = f"{aid} | {artist} - {aname}"
    
    if 'Various' in artist or 'Various' in aname:
        categories['合辑/Various Artists'].append(key)
    elif artist in mainstream_artists or any(a in artist for a in mainstream_artists):
        categories['华语主流（有希望）'].append(key)
    elif any(x in artist for x in ['刺猬', '声音碎片', '大忘杠', '大波浪', '葬尸湖', '惘闻', '天鹅与花朵', '郑宜农', '苏紫旭']):
        categories['华语独立（难）'].append(key)
    elif any(x in artist for x in ['Ira Dot', 'Lay Lady Lay', 'Honeyed', 'Cest La Vie', 'In Blue Time']):
        categories['外语独立（难）'].append(key)
    elif any(x in aname for x in ['翻唱', '现场', '演唱会', 'Cover', 'Help']):
        categories['翻唱/现场（难）'].append(key)
    else:
        categories['华语独立（难）'].append(key)

print("=" * 60)
print(f"MBID 缺失分析：共 {len(rows)} 张")
print("=" * 60)

for cat, items in categories.items():
    print(f"\n【{cat}】{len(items)} 张")
    for item in items[:10]:  # 每类只显示前10张
        print(f"  {item}")
    if len(items) > 10:
        print(f"  ... 还有 {len(items)-10} 张")

print(f"\n建议策略：")
print(f"  1. 华语主流 {len(categories['华语主流（有希望）'])} 张 → 优先手动查 MusicBrainz")
print(f"  2. 合辑 → 可能需要手动创建 release")
print(f"  3. 独立/难匹配 → 跳过或手动核查")
