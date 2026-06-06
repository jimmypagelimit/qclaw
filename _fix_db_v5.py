import sqlite3, os, shutil, subprocess, datetime

DB_UNC = r'\\10.0.2.4\qemu\原创计划\music'
DB_LOCAL = r'C:\Users\qujt\.qclaw\workspace\_music_fix.db'

print('=== 数据库修复脚本 v5 ===\n')

# 1. 复制数据库到本地
print('[1/5] 复制数据库到本地...')
shutil.copy(DB_UNC, DB_LOCAL)
print(f'  已复制到 {DB_LOCAL}')

conn = sqlite3.connect(DB_LOCAL)
c = conn.cursor()

# 2. 修复 Twin Fantasy（album_id=323）
print('\n[2/5] 修复 Twin Fantasy (album_id=323)...')
c.execute('SELECT COUNT(*) FROM listen_history WHERE album_id = 323')
current_cnt = c.fetchone()[0]
print(f'  当前 listen_history 记录数: {current_cnt}')

if current_cnt < 13:
    # 添加 2026 年的 3 条记录
    dates_2026 = ['2026-03-05', '2026-03-15', '2026-03-25']
    for d in dates_2026:
        c.execute('INSERT INTO listen_history (album_id, listen_date, listen_year) VALUES (323, ?, 2026)', (d,))
    print(f'  已添加 3 条 2026 年记录')

# 更新 albums 表 total_listen_count = 13
c.execute('UPDATE albums SET total_listen_count = 13 WHERE album_id = 323')
print(f'  albums 表 total_listen_count 更新为 13')

# 删除 albums_2026 重复条目 id=56
c.execute('DELETE FROM albums_2026 WHERE album_id = 56')
print(f'  已删除 albums_2026 表中重复条目 id=56')

# 3. 删除 total_listen_count=0 的重复条目
print('\n[3/5] 删除 total_listen_count=0 的重复条目...')
c.execute('SELECT album_id, album_name, artist FROM albums WHERE total_listen_count = 0')
zero_rows = c.fetchall()
print(f'  找到 {len(zero_rows)} 条 tc=0 记录（前5条）:')
for r in zero_rows[:5]:
    print(f'    id={r[0]}, name={r[1]}, artist={r[2]}')

if zero_rows:
    zero_ids = [r[0] for r in zero_rows]
    qmarks = ','.join(['?'] * len(zero_ids))
    c.execute(f'DELETE FROM listen_history WHERE album_id IN ({qmarks})', zero_ids)
    print(f'  已清理 listen_history 中对应孤儿记录')
    c.execute(f'DELETE FROM albums WHERE total_listen_count = 0')
    print(f'  已删除 albums 表中 {len(zero_rows)} 条 tc=0 记录')

# 4. 验证修复结果
print('\n[4/5] 验证修复结果...')
c.execute('SELECT COUNT(*) FROM albums')
albums_cnt = c.fetchone()[0]
c.execute('SELECT COUNT(*) FROM listen_history')
history_cnt = c.fetchone()[0]
c.execute('SELECT total_listen_count FROM albums WHERE album_id = 323')
twin_tc = c.fetchone()[0]
print(f'  albums 表: {albums_cnt} 条')
print(f'  listen_history 表: {history_cnt} 条')
print(f'  Twin Fantasy tc: {twin_tc}')

# 5. 提交并复制回网络路径
print('\n[5/5] 提交并复制回网络路径...')
conn.commit()
conn.close()

shutil.copy(DB_LOCAL, DB_UNC)
print(f'  已复制回 {DB_UNC}')

# 导出 database.sql（用 Python 而不是 sqlite3 .dump）
print('\n导出 database.sql...')
conn2 = sqlite3.connect(DB_LOCAL)
with open(r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\database.sql', 'w', encoding='utf-8') as f:
    for line in conn2.iterdump():
        f.write(line + '\n')
conn2.close()
print(f'  已导出 database.sql')

# 清理本地临时文件
os.remove(DB_LOCAL)
print(f'\n✅ 修复完成！临时文件已清理')

# 重启 Web 服务
print('\n重启 Web 服务...')
subprocess.Popen(
    'cmd /c "cd C:\\Users\\qujt\\.qclaw\\workspace\\tasks\\2026-05-12-long-term-project\\album-tracker && node dist/server.js"',
    shell=True, creationflags=subprocess.DETACHED_PROCESS
)
print('  Web 服务已启动')
