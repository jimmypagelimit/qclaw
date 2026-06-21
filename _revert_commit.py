import sqlite3, subprocess, os

# 导出 SQL
db = sqlite3.connect(r'C:\Users\qujt\.qclaw\workspace\_music_latest.db')
with open(r'C:\Users\qujt\.qclaw\workspace\_music_latest.sql', 'w', encoding='utf-8') as f:
    for line in db.iterdump():
        f.write(line + '\n')
db.close()
print("SQL exported")

# 重启 Web 服务
workdir = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker'
subprocess.Popen(['node', 'dist/server.js'], cwd=workdir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print("Web service restarted")

# Git commit + push
script = """cd /c/Users/qujt/.qclaw/workspace
git add -A
git commit -m "Revert: remove Snail Mail albums (user request)"
git push"""
with open(r'C:\Users\qujt\.qclaw\workspace\_git_revert.sh', 'w') as f:
    f.write(script)
print("Git script written")
