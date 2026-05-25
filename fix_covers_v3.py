#!/usr/bin/env python3
import sqlite3
import os
import subprocess
import time

DB_PATH = "G:/原创计划/music"
COVERS_DIR = r"C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\covers"
PROJECT_DIR = r"C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker"

# Step 1: connect DB, clear ALL cover_image_url (brute force fix)
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Check how many albums have cover_image_url set
c.execute("SELECT COUNT(*) FROM albums WHERE cover_image_url IS NOT NULL AND cover_image_url != ''")
count_before = c.fetchone()[0]
print(f"Albums with cover_image_url set: {count_before}")

# BRUTE FORCE: clear all cover_image_url to force re-download
c.execute("UPDATE albums SET cover_image_url = NULL")
conn.commit()
print("Cleared all cover_image_url from albums table")

# Also clear from year tables
for yt in ['albums_2024', 'albums_2025', 'albums_2026']:
    try:
        c.execute(f"UPDATE {yt} SET cover_image_url = NULL")
        print(f"  Cleared {yt}")
    except:
        pass
conn.commit()
conn.close()
print("DB cleared. Starting download...")

# Step 2: run download script
os.chdir(PROJECT_DIR)
with open("dl_log.txt", "w", encoding="utf-8") as log:
    result = subprocess.run(
        ["node", "dist/download-covers.js", "--count", "20"],
        stdout=log, stderr=log, text=True, encoding="utf-8"
    )

# Read log
with open("dl_log.txt", "r", encoding="utf-8") as f:
    log_content = f.read()
print("Download log:")
print(log_content[:3000])

# Step 3: check covers directory
if os.path.exists(COVERS_DIR):
    files = os.listdir(COVERS_DIR)
    print(f"Covers directory has {len(files)} files")
    if files:
        print("Sample:", files[:3])
else:
    print("Covers directory does NOT exist!")

# Step 4: restart server
print("Restarting web server...")
env = os.environ.copy()
env["SQLITE_PATH"] = DB_PATH
subprocess.Popen(
    ["node", "dist/server.js"],
    env=env,
    cwd=PROJECT_DIR,
    creationflags=subprocess.CREATE_NEW_CONSOLE
)
time.sleep(5)
print("Done! Server restarted. Check http://localhost:3456")
