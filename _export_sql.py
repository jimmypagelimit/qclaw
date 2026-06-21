import sqlite3
db = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
out = r'C:\Users\qujt\.qclaw\workspace\database.sql'
conn = sqlite3.connect(db)
f = open(out, 'w', encoding='utf-8')
for row in conn.iterdump():
    f.write(row[0] + '\n')
f.close()
conn.close()
print('SQL exported')
