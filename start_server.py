#!/usr/bin/env python3
import subprocess
import os
import time

DB_PATH = "G:/原创计划/music"
PROJECT_DIR = r"C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker"

# Start server
env = os.environ.copy()
env["SQLITE_PATH"] = DB_PATH
subprocess.Popen(
    ["node", "dist/server.js"],
    env=env,
    cwd=PROJECT_DIR,
    creationflags=subprocess.CREATE_NEW_CONSOLE
)
time.sleep(3)
print("Server started at http://localhost:3456")