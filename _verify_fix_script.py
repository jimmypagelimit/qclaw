import sqlite3

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
c = conn.cursor()

with open(r'C:\Users\qujt\.qclaw\workspace\_verify_fix.txt', 'w', encoding='utf-8') as f:
    f.write('=== 剩余非中文 Country 值 ===\n')
    c.execute('SELECT country, COUNT(*) FROM albums WHERE country IS NOT NULL GROUP BY country ORDER BY COUNT(*) DESC')
    for row in c.fetchall():
        country = row[0]
        count = row[1]
        f.write(f'  {repr(country)}: {count}\n')
        if country and not all('\u4e00' <= ch <= '\u9fff' or ch in '（）-、，。' for ch in country):
            f.write(f'    ^^^ NON-CHINESE\n')
    
    f.write('\n=== Region 中的异常值 ===\n')
    c.execute("SELECT region, COUNT(*) FROM albums WHERE region IS NOT NULL GROUP BY region ORDER BY COUNT(*) DESC")
    for row in c.fetchall():
        region = row[0]
        count = row[1]
        f.write(f'  {repr(region)}: {count}\n')

conn.close()
print('Done - check _verify_fix.txt')
