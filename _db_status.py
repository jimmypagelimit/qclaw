import sqlite3

db = r'\\10.0.2.4\qemu\原创计划\music'
conn = sqlite3.connect(db)
cur = conn.cursor()

# 总表统计
cur.execute('SELECT COUNT(*) FROM albums')
total = cur.fetchone()[0]
print(f'albums总数: {total}')

# 年度表
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'albums_2%'")
tables = sorted([r[0] for r in cur.fetchall()])
print(f'年度表: {tables}')

for t in tables:
    cur.execute(f'SELECT COUNT(*) FROM {t}')
    cnt = cur.fetchone()[0]
    print(f'  {t}: {cnt}条')

# 总听歌次数
cur.execute('SELECT SUM(total_listen_count) FROM albums')
tc = cur.fetchone()[0]
print(f'总听歌次数: {tc}')

conn.close()
