import subprocess, time
p = subprocess.Popen(['node', '-e', 'require("./dist/server.js")'],
    cwd=r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker',
    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
time.sleep(3)
err = p.stderr.read(2000).decode('utf-8', errors='replace')
if err:
    print('SYNTAX ERROR:', err[:500])
else:
    print('Syntax OK')
