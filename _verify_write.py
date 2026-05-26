import sqlite3

db = r'\\10.0.2.4\qemu\原创计划\music'
conn = sqlite3.connect(db)
c = conn.cursor()

with open(r'C:\Users\qujt\.qclaw\workspace\_verify_output.txt', 'w', encoding='utf-8') as f:
    f.write('转换后的记录:\n')
    c.execute('SELECT album_id, album_name, artist FROM albums WHERE album_id IN (306, 539)')
    for row in c.fetchall():
        f.write(f'  albums {row[0]}: {row[2]} - {row[1]}\n')
    
    c.execute('SELECT album_id, album_name, artist FROM albums_2026 WHERE album_id = 195')
    for row in c.fetchall():
        f.write(f'  albums_2026 {row[0]}: {row[2]} - {row[1]}\n')
    
    f.write('\n含"著"字符的记录（需人工核对）:\n')
    c.execute("SELECT album_id, album_name, artist FROM albums WHERE album_name LIKE '%著%' OR artist LIKE '%著%'")
    count = 0
    for row in c.fetchall():
        f.write(f'  albums {row[0]}: {row[2]} - {row[1]}\n')
        count += 1
    if count == 0:
        f.write('  (无)\n')
    
    f.write('\n验证完成\n')

conn.close()
print('Verification output written to file')
