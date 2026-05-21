import subprocess, sys, os, time

# 项目路径
project_dir = r'C:\Users\15206\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker'
os.chdir(project_dir)

# 检查是否已有 node 进程占用 3456
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
result = sock.connect_ex(('127.0.0.1', 3456))
sock.close()

if result == 0:
    print("Port 3456 is already in use")
    sys.exit(1)
else:
    print("Port 3456 is free, starting server...")

# 启动服务器
proc = subprocess.Popen(
    ['node', 'dist/server.js'],
    cwd=project_dir,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    encoding='utf-8'
)

# 等待启动
time.sleep(3)

# 验证
try:
    from urllib.request import urlopen
    resp = urlopen('http://localhost:3456/', timeout=3)
    print(f"Server started successfully! Status: {resp.status}")
except Exception as e:
    print(f"Server may not be ready: {e}")
    # 打印进程输出
    if proc.stdout:
        out = proc.stdout.read()
        print(f"Process output: {out[:500]}")
