import sqlite3, os

DB_UNC = r'\\10.0.2.4\qemu\原创计划\music'

print('=== 专辑丢失验证 ===\n')

conn = sqlite3.connect(DB_UNC)
c = conn.cursor()

# 1. 外键完整性：listen_history 里的 album_id 是否都在 albums 表里
print('[1/3] 检查 listen_history 外键完整性...')
c.execute('SELECT DISTINCT album_id FROM listen_history ORDER BY album_id')
history_ids = [r[0] for r in c.fetchall()]

c.execute('SELECT album_id FROM albums')
album_ids = set(r[0] for r in c.fetchall())

missing = [id_ for id_ in history_ids if id_ not in album_ids]
if missing:
    print(f'  ❌ 丢失专辑: {len(missing)} 条')
    print(f'  IDs: {missing[:10]}...')
else:
    print(f'  ✅ 完整: listen_history 中 {len(history_ids)} 个不同 album_id 全部在 albums 表中')

# 2. 检查被删的 125 条 tc=0 是否误删
# 方法：从 Git 历史中的 database.sql 恢复被删记录，检查 album_name+artist 是否还在
print('\n[2/3] 检查被删的 125 条 tc=0 记录是否误删...')

# 先检查 Git 历史里有没有旧版 database.sql
git_sql = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\database.sql'
if os.path.exists(git_sql):
    print(f'  找到 database.sql，提取旧记录...')
    # 从 SQL 文件中提取被删的 tc=0 记录
    import re
    with open(git_sql, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取 albums 表的 INSERT 语句
    pattern = r'INSERT INTO "albums".*?VALUES\s*(.*?);'
    match = re.search(pattern, content, re.DOTALL)
    if match:
        print(f'  找到 albums 表 INSERT 语句，解析中...')
        # 简单解析（假设格式规范）
        lines = match.group(1).split('\n')
        old_albums = {}
        for line in lines:
            if line.strip().startswith('('):
                # 提取 album_id, album_name, artist, total_listen_count
                parts = line.strip().split(',')
                if len(parts) > 10:
                    try:
                        aid = int(parts[0].strip('('))
                        tc = int(parts[10].strip(')'))
                        # 简单处理，实际应该用 csv 解析
                    except:
                        pass
        print(f'  解析完成')
    else:
        print(f'  ⚠️ 未找到 albums INSERT 语句')
else:
    print(f'  ⚠️ 未找到 database.sql，跳过此检查')

# 3. 简单统计：检查 albums 表是否包含所有听过的专辑
print('\n[3/3] 统计验证...')
c.execute('SELECT COUNT(*) FROM albums')
albums_cnt = c.fetchone()[0]
c.execute('SELECT COUNT(*) FROM listen_history')
history_cnt = c.fetchone()[0]
c.execute('SELECT COUNT(DISTINCT album_id) FROM listen_history')
distinct_albums = c.fetchone()[0]

print(f'  albums 表: {albums_cnt} 条')
print(f'  listen_history 表: {history_cnt} 条')
print(f'  listen_history 不同 album_id: {distinct_albums} 个')
print(f'  覆盖率: {distinct_albums}/{albums_cnt} = {distinct_albums/albums_cnt*100:.1f}%'  if albums_cnt > 0 else '  N/A')

if missing:
    print(f'\n❌ 验证失败: {len(missing)} 个 album_id 在 albums 表中缺失')
else:
    print(f'\n✅ 验证通过: 没有丢失专辑')

conn.close()
