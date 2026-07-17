import subprocess, time, sys

# Kill existing node
subprocess.run('taskkill /F /IM node.exe 2>nul', shell=True)
time.sleep(1)

# Start
workdir = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker'
p = subprocess.Popen(
    ['node', 'dist/server.js'],
    cwd=workdir,
    creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)
print(f'Started PID={p.pid}')
