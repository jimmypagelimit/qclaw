#!/usr/bin/env python3
"""Batch download album covers - stops server, downloads, restarts."""
import subprocess, os, time, sqlite3

DB_PATH = "G:/原创计划/music"
PROJECT_DIR = r"C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker"
COVERS_DIR = os.path.join(PROJECT_DIR, "covers")

# 1. Check how many still missing
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("SELECT COUNT(*) FROM albums WHERE cover_image_url IS NULL OR cover_image_url = ''")
missing = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM albums WHERE cover_image_url IS NOT NULL AND cover_image_url != ''")
has_cover = c.fetchone()[0]
conn.close()
print(f"DB status: {has_cover} with cover_url, {missing} missing cover_url")
print(f"Covers dir: {len(os.listdir(COVERS_DIR))} files")

# 2. Kill server
subprocess.run(["taskkill", "/f", "/im", "node.exe"], capture_output=True)
time.sleep(2)

# 3. Download in batches of 50
os.chdir(PROJECT_DIR)
total_downloaded = 0
for i in range(20):  # max 20 batches = 1000 covers
    with open(f"dl_batch_{i}.txt", "w", encoding="utf-8") as log:
        result = subprocess.run(
            ["node", "dist/download-covers.js", "--count", "50"],
            stdout=log, stderr=log, text=True, encoding="utf-8"
        )
    with open(f"dl_batch_{i}.txt", "r", encoding="utf-8") as f:
        content = f.read()
    # Parse result line
    if "0 \u603b\u8ba1" in content or "/ 0 " in content:
        print(f"Batch {i}: no more albums to download, stopping")
        break
    # Extract count
    import re
    m = re.search(r'(\d+) \u6210\u529f', content)
    if m:
        batch_ok = int(m.group(1))
        total_downloaded += batch_ok
        print(f"Batch {i}: downloaded {batch_ok}, total {total_downloaded}")
    else:
        print(f"Batch {i}: {content[:200]}")
        break
    if batch_ok == 0:
        break
    time.sleep(1)

# 4. Final count
final_files = len(os.listdir(COVERS_DIR)) if os.path.exists(COVERS_DIR) else 0
print(f"\nTotal covers on disk: {final_files}")

# 5. Restart server
env = os.environ.copy()
env["SQLITE_PATH"] = DB_PATH
subprocess.Popen(
    ["node", "dist/server.js"],
    env=env,
    cwd=PROJECT_DIR,
    creationflags=subprocess.CREATE_NEW_CONSOLE
)
time.sleep(3)
print("Server restarted at http://localhost:3456")
