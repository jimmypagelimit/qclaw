import psutil, time, os, subprocess, sys

port = 3456

# Kill existing server on port
killed = False
for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        for conn in proc.net_connections():
            if conn.laddr.port == port:
                print(f'Killing PID {proc.pid}')
                proc.kill()
                killed = True
    except:
        pass

time.sleep(1)

# Start new server
bat = r'C:\Users\15206\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\start_server.bat'
subprocess.Popen(['cmd', '/c', 'start', '/b', 'cmd', '/c', bat],
                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                 creationflags=subprocess.CREATE_NO_WINDOW)
print('Server restarted on port 3456')