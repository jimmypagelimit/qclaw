import subprocess, time, os

# 杀旧进程
os.system("taskkill /f /im node.exe >nul 2>&1")
time.sleep(1)

# 启动服务
cwd = r"C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker"
print(f"Starting server in: {cwd}")
p = subprocess.Popen(["node", "dist/server.js"], cwd=cwd)
print(f"Server PID: {p.pid}")
print("Check http://localhost:3456")
# 保持进程
p.wait()
