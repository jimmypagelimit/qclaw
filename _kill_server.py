import socket, os, time
# Kill process on port 3456
import subprocess
result = subprocess.run(['cmd', '/c', 'netstat -ano'], capture_output=True, text=True)
for line in result.stdout.splitlines():
    if ':3456' in line and 'LISTENING' in line:
        pid = line.split()[-1]
        print(f'Killing PID {pid}')
        subprocess.run(['cmd', '/c', f'taskkill /F /PID {pid}'], capture_output=True)
        break
