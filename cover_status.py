#!/usr/bin/env python3
import sqlite3, os

DB = "G:/原创计划/music"
conn = sqlite3.connect(DB)
c = conn.cursor()
c.execute("SELECT COUNT(*) FROM albums WHERE cover_image_url IS NOT NULL AND cover_image_url != ''")
with_url = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM albums")
total = c.fetchone()[0]
conn.close()

cov = r"C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\covers"
files = len(os.listdir(cov)) if os.path.exists(cov) else 0

print(f"Total albums: {total}")
print(f"With cover_url: {with_url}")
print(f"Missing cover_url: {total - with_url}")
print(f"Files on disk: {files}")
print(f"Coverage: {with_url/total*100:.1f}%")