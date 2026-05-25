#!/usr/bin/env python3
import subprocess, os, time

DB = "G:/原创计划/music"
PROJECT = r"C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker"

env = os.environ.copy()
env["SQLITE_PATH"] = DB
subprocess.Popen(
    ["node", "dist/server.js"],
    env=env,
    cwd=PROJECT,
    creationflags=subprocess.CREATE_NEW_CONSOLE
)
time.sleep(3)
print("Server at http://localhost:3456")