"""
Pitchfork Expert 深化探索 - 会话总结
"""
import sqlite3, subprocess, json
from datetime import datetime

DB_PATH = r"C:\Users\qujt\.qclaw\workspace\_music_latest.db"

# DB stats
conn = sqlite3.connect(DB_PATH)
with_pf = conn.execute("SELECT COUNT(*) FROM albums WHERE pitchfork_score IS NOT NULL").fetchone()[0]
bnm = conn.execute("SELECT COUNT(*) FROM albums WHERE pitchfork_score >= 8.0").fetchone()[0]
top = conn.execute("SELECT artist, album_name, pitchfork_score FROM albums WHERE pitchfork_score IS NOT NULL ORDER BY pitchfork_score DESC LIMIT 10").fetchall()

# Project files
import os
pf_dir = r"C:\Users\qujt\.qclaw\workspace\tasks\pitchfork-expert"
py_files = [f for f in os.listdir(pf_dir) if f.endswith('.py')]
data_files = []
for root, dirs, files in os.walk(os.path.join(pf_dir, 'data')):
    for f in files:
        data_files.append(os.path.relpath(os.path.join(root, f), pf_dir))
doc_files = []
for root, dirs, files in os.walk(os.path.join(pf_dir, 'docs')):
    for f in files:
        doc_files.append(os.path.relpath(os.path.join(root, f), pf_dir))

print(f"=== Pitchfork Expert 深化探索总结 ===")
print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
print()
print("[DB] 数据库状态:")
print(f"   有 PF 评分的专辑: {with_pf}")
print(f"   BNM (≥8.0): {bnm}")
print(f"   最高分 Top 5:")
for r in top[:5]:
    print(f"      {r[2]} | {r[0]} — {r[1]}")

print()
print(f"[Py] Python 脚本 ({len(py_files)}):")
for f in sorted(py_files):
    size = os.path.getsize(os.path.join(pf_dir, f))
    print(f"   {f} ({size} bytes)")

print()
print(f"[Data] 数据文件 ({len(data_files)}):")
for f in data_files:
    print(f"   {f}")

print()
print(f"[Doc] 知识库文档 ({len(doc_files)}):")
for f in doc_files:
    size = os.path.getsize(os.path.join(pf_dir, f))
    print(f"   {f} ({size} bytes)")

conn.close()
