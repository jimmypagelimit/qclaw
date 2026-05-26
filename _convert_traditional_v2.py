import sqlite3

# 明确可安全转换的繁体 -> 简体映射（无歧义字符）
t2s_map = {
    '並': '并', '於': '于', '與': '与', '體': '体',
    '會': '会', '術': '术', '發': '发', '現': '现',
    '時': '时', '後': '后', '處': '处',
    '點': '点', '線': '线', '經': '经', '歷': '历', '區': '区',
    '學': '学', '門': '门', '開': '开', '關': '关', '間': '间',
    '從': '从', '來': '来', '國': '国', '際': '际', '語': '语',
    '說': '说', '話': '话', '請': '请', '問': '问',
    '應': '应', '當': '当', '這': '这', '裡': '里',
    '麼': '么', '們': '们',
    '遺': '遗', '餘': '余', '僅': '仅', '將': '将',
    '萬': '万', '書': '书', '專': '专',
    '義': '义', '罰': '罚', '羣': '群',
    '冊': '册', '隻': '只', '摺': '折',
    # '著' 有歧义，不在此表转换，需人工核对
}

def convert_to_simplified(text):
    """将繁体中文转换为简体（仅转换无歧义字符）"""
    result = []
    for char in text:
        result.append(t2s_map.get(char, char))
    return ''.join(result)

db = r'\\10.0.2.4\qemu\原创计划\music'
conn = sqlite3.connect(db)
c = conn.cursor()

updates = []

# 检查 albums 表
print('=== 检查 albums 表 ===')
c.execute('SELECT album_id, album_name, artist FROM albums')
for row in c.fetchall():
    album_id, album_name, artist = row
    new_name = convert_to_simplified(album_name)
    new_artist = convert_to_simplified(artist)
    if new_name != album_name or new_artist != artist:
        print(f'ID {album_id}:')
        print(f'  旧: {artist} - {album_name}')
        print(f'  新: {new_artist} - {new_name}')
        updates.append((new_name, new_artist, album_id, 'albums'))

# 检查 albums_2026 表
print('\n=== 检查 albums_2026 表 ===')
c.execute('SELECT album_id, album_name, artist FROM albums_2026')
for row in c.fetchall():
    album_id, album_name, artist = row
    new_name = convert_to_simplified(album_name)
    new_artist = convert_to_simplified(artist)
    if new_name != album_name or new_artist != artist:
        print(f'ID {album_id}:')
        print(f'  旧: {artist} - {album_name}')
        print(f'  新: {new_artist} - {new_name}')
        updates.append((new_name, new_artist, album_id, 'albums_2026'))

print(f'\n共找到 {len(updates)} 条需要转换的记录')

if updates:
    print('\n开始更新...')
    for new_name, new_artist, album_id, table in updates:
        c.execute(f'UPDATE {table} SET album_name = ?, artist = ? WHERE album_id = ?',
                  (new_name, new_artist, album_id))
        print(f'  {table} ID {album_id} 已更新')
    conn.commit()
    print('✅ 所有记录已更新')
else:
    print('✅ 没有需要转换的记录')

# 特别提示需要人工核对含'著'的记录
print('\n⚠️  以下记录含"著"字符，需人工核对是否需转换为"着":')
c.execute("SELECT album_id, album_name, artist FROM albums WHERE album_name LIKE '%著%' OR artist LIKE '%著%'")
for row in c.fetchall():
    print(f'  albums {row[0]}: {row[2]} - {row[1]}')
c.execute("SELECT album_id, album_name, artist FROM albums_2026 WHERE album_name LIKE '%著%' OR artist LIKE '%著%'")
for row in c.fetchall():
    print(f'  albums_2026 {row[0]}: {row[2]} - {row[1]}')

conn.close()
