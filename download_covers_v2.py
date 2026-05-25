#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import os
import sys

# Fix Windows console encoding issue
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

os.chdir(r"C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker")

# Run download script, capture output to file
print("开始下载封面...")
with open("download_log.txt", "w", encoding="utf-8") as log:
    result = subprocess.run(
        ["node", "dist/download-covers.js", "--count", "10"],
        stdout=log,
        stderr=log,
        text=True,
        encoding="utf-8"
    )

# Read log
with open("download_log.txt", "r", encoding="utf-8") as f:
    log_content = f.read()
    print("下载日志:")
    print(log_content[:2000])

# Check covers directory
covers_dir = "covers"
if os.path.exists(covers_dir):
    files = os.listdir(covers_dir)
    print(f"\n封面目录文件数: {len(files)}")
    if files:
        print("示例文件:", files[:3])
else:
    print("\n封面目录不存在!")

# Restart server
print("\n重启 Web 服务器...")
env = os.environ.copy()
env["SQLITE_PATH"] = r"G:\原创计划\music\music"
subprocess.Popen(
    ["node", "dist/server.js"],
    env=env,
    creationflags=subprocess.CREATE_NEW_CONSOLE
)
print("服务器已重启，等待 5 秒...")
import time
time.sleep(5)
print("完成!")
