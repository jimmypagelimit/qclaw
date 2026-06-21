import subprocess
import os

# 启动 Web 服务
workdir = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker'
cmd = ['node', 'dist/server.js']

# 在后台启动
process = subprocess.Popen(cmd, cwd=workdir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print(f"Web service started with PID: {process.pid}")
