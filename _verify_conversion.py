import sqlite3

db = r'\\10.0.2.4\qemu\原创计划\music'
conn = sqlite3.connect(db)
c = conn.cursor()

print('转换后的记录:')
c.execute('SELECT album_id, album_name, artist FROM albums WHERE album_id IN (306, 539)')
for row in c.fetchall():
    print(f'  albums {row[0]}: {row[2]} - {row[1]}')

c.execute('SELECT album_id, album_name, artist FROM albums_2026 WHERE album_id = 195')
for row in c.fetchall():
    print(f'  albums_2026 {row[0]}: {row[2]} - {row[1]}')

print()
print('含"著"字符的记录（需人工核对）:')
c.execute("SELECT album_id, album_name, artist FROM albums WHERE album_name LIKE '%著%' OR artist LIKE '%著%'")
count = 0
for row in c.fetchall():
    print(f'  albums {row[0]}: {row[2]} - {row[1]}')
    count += 1
if count == 0:
    print('  (无)')

conn.close()
print('\n验证完成')
