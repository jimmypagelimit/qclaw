import sqlite3

db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
conn = sqlite3.connect(db)
c = conn.cursor()

with open(r'C:\Users\qujt\.qclaw\workspace\_final_result.txt', 'w', encoding='utf-8') as f:
    f.write('=== Country 字段最终统计 ===\n')
    c.execute('SELECT COUNT(*) FROM albums WHERE country IS NOT NULL')
    f.write(f'非空: {c.fetchone()[0]}\n')
    c.execute('SELECT COUNT(*) FROM albums WHERE country IS NULL')
    f.write(f'NULL: {c.fetchone()[0]}\n')
    f.write('\n按国家分布:\n')
    c.execute('SELECT country, COUNT(*) FROM albums WHERE country IS NOT NULL GROUP BY country ORDER BY COUNT(*) DESC')
    for row in c.fetchall():
        f.write(f'  {row[0]}: {row[1]}\n')
    
    f.write('\n=== Region 字段最终统计 ===\n')
    c.execute('SELECT COUNT(*) FROM albums WHERE region IS NOT NULL')
    f.write(f'非空: {c.fetchone()[0]}\n')
    c.execute('SELECT COUNT(*) FROM albums WHERE region IS NULL')
    f.write(f'NULL: {c.fetchone()[0]}\n')
    f.write('\n按地区分布 (Top 20):\n')
    c.execute('SELECT region, COUNT(*) FROM albums WHERE region IS NOT NULL GROUP BY region ORDER BY COUNT(*) DESC')
    for i, row in enumerate(c.fetchall()):
        if i >= 20: break
        f.write(f'  {row[0]}: {row[1]}\n')
    
    f.write('\n=== 检查非中文 Country ===\n')
    c.execute('SELECT country, COUNT(*) FROM albums WHERE country IS NOT NULL GROUP BY country')
    for row in c.fetchall():
        country = row[0]
        if country and not all('\u4e00' <= ch <= '\u9fff' or ch in '（）-、，。' for ch in country):
            f.write(f'  WARNING: {repr(country)}: {row[1]}\n')
    f.write('  (无异常)\n')

conn.close()
print('Done - check _final_result.txt')
