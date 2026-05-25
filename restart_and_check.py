import sqlite3, os, time, subprocess, sys

DB = "G:/原创计划/music"
PROJECT = r"C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker"

# Check status
conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute("SELECT COUNT(*) FROM albums")
total = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM albums WHERE cover_image_url IS NOT NULL AND cover_image_url != ''")
with_url = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM albums WHERE cover_image_url IS NULL OR cover_image_url = ''")
missing = c.fetchone()[0]
conn.close()

covers_dir = os.path.join(PROJECT, "covers")
files = len(os.listdir(covers_dir)) if os.path.exists(covers_dir) else 0

print(f"Total albums: {total}")
print(f"With cover: {with_url} ({with_url/total*100:.1f}%)")
print(f"Missing: {missing}")
print(f"Files on disk: {files}")

# Restart server
env = os.environ.copy()
env["SQLITE_PATH"] = DB
subprocess.Popen(
    ["node", "dist/server.js"],
    env=env,
    cwd=PROJECT,
    creationflags=subprocess.CREATE_NEW_CONSOLE
)
time.sleep(3)
print("Server restarted: http://localhost:3456")
