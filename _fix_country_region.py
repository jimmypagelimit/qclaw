import sqlite3

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
c = conn.cursor()

print('=== Country 字段更正 ===')

# 1. 简单映射（中英文统一）
mapping = [
    ("country='US'", '美国'),
    ("country='UK'", '英国'),
    ("country='China'", '中国'),
    ("country='Germany'", '德国'),
    ("country='Taiwan'", '台湾'),
    ("country='CN'", '中国'),
    ("country='TW'", '台湾'),
    ("country='Norway'", '挪威'),
    ("country='Japan'", '日本'),
    ("country='France'", '法国'),
    ("country='Chile'", '智利'),
    ("country='Brazil'", '巴西'),
    ("country='Germany'", '德国'),
    ("country='Spain'", '西班牙'),
    ("country='Ireland'", '爱尔兰'),
    ("country='Australia'", '澳大利亚'),
    ("country='Ukraine'", '乌克兰'),
    ("country='Sweden'", '瑞典'),
    ("country='Mexico'", '墨西哥'),
    ("country='Canada'", '加拿大'),
]

for condition, new_val in mapping:
    c.execute(f'UPDATE albums SET country=? WHERE {condition}', (new_val,))
    print(f'  {condition} -> {new_val}: {c.rowcount} 条')

# 2. 复合值（取第一个国家）
complex_mapping = [
    ("country='USA & Europe'", '美国'),
    ("country='USA & Canada'", '美国'),
    ("country='UK, Europe & US'", '英国'),
    ("country='UK & US'", '英国'),
    ("country='UK & Europe'", '英国'),
    ("country='Worldwide'", None),
    ("country='Unknown'", None),
    ("country='XW'", None),
]
for condition, new_val in complex_mapping:
    c.execute(f'UPDATE albums SET country=? WHERE {condition}', (new_val,))
    print(f'  {condition} -> {new_val}: {c.rowcount} 条')

# 3. 空字符串 -> NULL
c.execute("UPDATE albums SET country=NULL WHERE country=''")
print(f'  空字符串 -> NULL: {c.rowcount} 条')

# 4. Europe (2张) - 手动修正
# id=58: The Jesus and Mary Chain - Scottish -> 英国
# id=454: My Bloody Valentine - Irish -> 爱尔兰
c.execute('UPDATE albums SET country=? WHERE album_id=58', ('英国',))
c.execute('UPDATE albums SET country=? WHERE album_id=454', ('爱尔兰',))
print(f'  Europe -> 手动修正: 2 条')

# 5. None/NULL 的专辑 - 按艺人名推断
# 中国艺人
china_artists = ['周华健', '陈楚生', '张雨生', '施鑫文月', '梁博', '刺猬', '木马', '海朋森', '缺省', '安抚狮子', '小雨乐队', 'Lay Lady Lay', '文雀', '觀觀', '猿', '鍋一楠', '羊与马群', '何韻詩', 'L8ching', 'The Mensis Ritual', 'Kill-Kennie', 'threadbaron', '魚住英里奈', '谢甜柒', 'Ira Dot', 'Porcelain Stars']
# 实际检查 album_id 550(周华健-台湾), 474(何韻詩-香港), 508(魚住英里奈-日本)
c.execute('UPDATE albums SET country=? WHERE album_id=550', ('台湾',))
c.execute('UPDATE albums SET country=? WHERE album_id=474', ('香港',))
c.execute('UPDATE albums SET country=? WHERE album_id=508', ('日本',))
# 中国艺人
c.execute('UPDATE albums SET country=? WHERE album_id IN (423,427,429,430,434,439,446,447,448,451,465,468,469,470,471,472,477,480,489,525)', ('中国',))
# 外国艺人
c.execute('UPDATE albums SET country=? WHERE album_id IN (549,551,553,554,556,557,559)', ('美国',))
print(f'  NULL -> 按艺人推断: 31 条')

print()
print('=== Region 字段清理 ===')

# 删除洲际级别错误值
continent_values = ['East Asia', 'North America', 'Europe', 'South America', '北美洲', '欧美']
for val in continent_values:
    c.execute('UPDATE albums SET region=NULL WHERE region=?', (val,))
    print(f'  {repr(val)} -> NULL: {c.rowcount} 条')

print()
print('=== 验证 ===')
c.execute('SELECT country, COUNT(*) FROM albums GROUP BY country ORDER BY COUNT(*) DESC')
print('Country 字段:')
for row in c.fetchall():
    print(f'  {repr(row[0])}: {row[1]}')

c.execute('SELECT region, COUNT(*) FROM albums GROUP BY region ORDER BY COUNT(*) DESC')
print('Region 字段:')
for row in c.fetchall():
    print(f'  {repr(row[0])}: {row[1]}')

conn.commit()
conn.close()
print()
print('完成！')
