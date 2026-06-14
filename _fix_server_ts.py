#!/usr/bin/env python3
"""
修复 server.ts 中所有 total_listen_count 引用
改为 JOIN listen_history 动态计算
用法：C:\Python311\python.exe fix_server_ts.py
"""
import re

SERVER_TS = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\src\server.ts'

with open(SERVER_TS, 'r', encoding='utf-8') as f:
    content = f.read()

original = content

# 修复 1: stats 接口的 totalListens 查询（SUM total_listen_count → COUNT listen_history）
old1 = "'SELECT COALESCE(SUM(total_listen_count), 0) as total FROM albums'"
new1 = "'SELECT COUNT(*) as total FROM listen_history'"
content = content.replace(old1, new1)

# 修复 2: stats 接口的 topAlbum 查询（ORDER BY total_listen_count → JOIN 计算）
old2 = "'SELECT * FROM albums ORDER BY total_listen_count DESC LIMIT 1'"
new2 = """`SELECT a.*, COUNT(lh.id) as cnt 
         FROM albums a 
         LEFT JOIN listen_history lh ON a.album_id = lh.album_id 
         GROUP BY a.album_id 
         ORDER BY cnt DESC LIMIT 1`"""
content = content.replace(old2, new2)

# 修复 3: sortMap 中的 a.total_listen_count → 子查询
old3 = "listen: yearNum ? 'year_listen_count' : 'a.total_listen_count',"
new3 = "listen: yearNum ? 'year_listen_count' : '(SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id)',"
content = content.replace(old3, new3)

# 修复 4: /api/artist/:name 接口的 ORDER BY total_listen_count
old4 = "'SELECT * FROM albums WHERE artist LIKE ? ORDER BY total_listen_count DESC LIMIT ?',"
new4 = """'SELECT a.*, (SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id) as cnt FROM albums a WHERE artist LIKE ? ORDER BY cnt DESC LIMIT ?',"""
content = content.replace(old4, new4)

# 修复 5: /api/top 非年份接口的 ORDER BY total_listen_count
old5 = "'SELECT * FROM albums ORDER BY total_listen_count DESC LIMIT ?',"
# 注意：这个在两个地方出现（top 接口和可能其他地方），需要精确匹配上下文
# 先检查
occurrences = [m.start() for m in re.finditer(re.escape(old5), content)]
print(f"修复 5 找到 {len(occurrences)} 处: {occurrences}")

if len(occurrences) == 1:
    new5 = """'SELECT a.*, (SELECT COUNT(*) FROM listen_history lh WHERE lh.album_id = a.album_id) as cnt FROM albums a ORDER BY cnt DESC LIMIT ?',"""
    content = content.replace(old5, new5)
else:
    print("  警告：多处匹配，需要手动检查")

# 检查是否还有遗漏
remaining = [m.start() for m in re.finditer(r'total_listen_count', content)]
if remaining:
    print(f"\n警告：还有 {len(remaining)} 处未修复: {remaining}")
else:
    print("\n所有 total_listen_count 引用已修复")

# 保存
with open(SERVER_TS, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n完成：{SERVER_TS}")
print(f"字符变化：{len(original)} → {len(content)}")
