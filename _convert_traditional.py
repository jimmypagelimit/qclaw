import sqlite3

# 繁体 -> 简体映射表（常用字）
t2s_map = {
    '著': '着', '並': '并', '於': '于', '與': '与', '體': '体',
    '會': '会', '藝': '艺', '術': '术', '發': '发', '現': '现',
    '時': '时', '候': '候', '後': '后', '前': '前', '處': '处',
    '點': '点', '線': '线', '經': '经', '歷': '历', '區': '区',
    '學': '学', '門': '门', '開': '开', '關': '关', '間': '间',
    '從': '从', '來': '来', '國': '国', '際': '际', '語': '语',
    '說': '说', '話': '话', '請': '请', '問': '问', '答': '答',
    '應': '应', '當': '当', '這': '这', '那': '那', '裡': '里',
    '麼': '么', '什': '什', '麼': '么', '們': '们', '的': '的',
    '是': '是', '不': '不', '了': '了', '在': '在', '有': '有',
    '我': '我', '你': '你', '他': '他', '她': '她', '它': '它',
    '們': '们', '的': '的', '是': '是', '不': '不', '了': '了',
}

def convert_to_simplified(text):
    """将繁体中文转换为简体"""
    result = []
    for char in text:
        result.append(t2s_map.get(char, char))
    return ''.join(result)

db = r'\\10.0.2.4\qemu\原创计划\music'
conn = sqlite3.connect(db)
c = conn.cursor()

# 检查 albums 表
print('=== 检查 albums 表 ===')
c.execute('SELECT album_id, album_name, artist FROM albums')
updates = []
for row in c.fetchall():
    album_id, album_name, artist = row
    new_name = convert_to_simplified(album_name)
    new_artist = convert_to_simplified(artist)
    if new_name != album_name or new_artist != artist:
        print(f'ID {album_id}:')
        print(f'  旧: {artist} - {album_name}')
        print(f'  新: {new_artist} - {new_name}')
        updates.append((album_id, new_name, new_artist, 'albums'))

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
        updates.append((album_id, new_name, new_artist, 'albums_2026'))

print(f'\n共找到 {len(updates)} 条需要转换的记录')

# 执行更新
if updates:
    print('\n开始更新...')
    for album_id, new_name, new_artist, table in updates:
        c.execute(f'UPDATE {table} SET album_name = ?, artist = ? WHERE album_id = ?',
                  (new_name, new_artist, album_id))
        print(f'  {table} ID {album_id} 已更新')
    conn.commit()
    print('✅ 所有记录已更新')
else:
    print('✅ 没有需要转换的记录')

conn.close()
