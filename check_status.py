import sqlite3, os
db = "G:/原创计划/music"
con = sqlite3.connect(db)
c = con.cursor()
c.execute("SELECT COUNT(*) FROM albums")
t = c.fetchone()[0]
c.execute("SELECT COUNT(*) FROM albums WHERE cover_image_url IS NOT NULL AND cover_image_url != ''")
w = c.fetchone()[0]
con.close()
covers = r"C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\covers"
files = len(os.listdir(covers))
print(f"Total: {t}")
print(f"With cover: {w} ({w/t*100:.1f}%)")
print(f"Missing: {t-w}")
print(f"Files on disk: {files}")