import subprocess, time, psutil, os, signal

# Kill existing node processes on port 3456
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        cmdline = ' '.join(proc.info['cmdline'] or [])
        if 'node' in proc.info['name'].lower() and '3456' in cmdline:
            print(f"Killing PID {proc.info['pid']}: {cmdline}")
            proc.kill()
    except:
        pass

time.sleep(1)

# Start server
os.chdir(r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker')
subprocess.Popen(['node', 'dist/server.js'], creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
print('Server started on http://localhost:3456')
