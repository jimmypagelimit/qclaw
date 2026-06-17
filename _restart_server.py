import subprocess, os, time

# 先杀旧进程
os.system("taskkill /f /im node.exe >nul 2>&1")
time.sleep(1)

# 启动服务
cwd = r"C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker"
node_exe = r"C:\Program Files\QClaw\v0.2.26.557\resources\openclaw\config\bin\node.exe"

# 验证路径
if not os.path.exists(node_exe):
    # 尝试找 node
    import shutil
    node_exe = shutil.which("node") or shutil.which("node.exe")
    print(f"node found at: {node_exe}")

print(f"Starting: {node_exe} dist/server.js")
print(f"cwd: {cwd}")

p = subprocess.Popen([node_exe, "dist/server.js"], cwd=cwd)
time.sleep(3)
print(f"Server PID: {p.pid}")
print("Check http://localhost:3456")
