import subprocess, time, os

# Start server
os.chdir(r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker')
proc = subprocess.Popen(['node', 'dist/server.js'], creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
print(f'Server started on http://localhost:3456 (PID {proc.pid})')
