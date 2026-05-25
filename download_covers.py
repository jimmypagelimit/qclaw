#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import subprocess
import os

os.chdir(r"C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker")

# Run download script
print("开始下载封面...")
result = subprocess.run(
    ["node", "dist/download-covers.js", "--count", "10"],
    capture_output=True,
    text=True,
    encoding="utf-8"
)
print("STDOUT:", result.stdout[:2000])
print("STDERR:", result.stderr[:1000])

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
print("服务器已重启")
