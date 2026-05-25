#!/usr/bin/env python3
import subprocess, os, time

os.chdir(r"C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker")

total_ok = 0
for i in range(15):
    with open(f"dl2_batch_{i}.txt", "w", encoding="utf-8") as log:
        result = subprocess.run(
            ["node", "dist/download-covers.js", "--count", "50"],
            stdout=log, stderr=log, text=True, encoding="utf-8"
        )
    with open(f"dl2_batch_{i}.txt", "r", encoding="utf-8") as f:
        out = f.read()
    
    import re
    m_ok = re.search(r'(\d+) \u6210\u529f', out)
    m_fail = re.search(r'(\d+) \u5931\u8d25', out)
    m_total = re.search(r'(\d+) \u603b\u8ba1', out)
    
    ok = int(m_ok.group(1)) if m_ok else 0
    fail = int(m_fail.group(1)) if m_fail else 0
    tot = int(m_total.group(1)) if m_total else 0
    total_ok += ok
    
    print(f"Batch {i}: ok={ok} fail={fail} total={tot} | cumulative_ok={total_ok}")
    
    if tot == 0:
        print("No more albums to process, stopping.")
        break
    time.sleep(2)

cov = "covers"
print(f"\nFinal covers on disk: {len(os.listdir(cov))}")
