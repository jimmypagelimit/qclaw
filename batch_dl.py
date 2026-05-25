#!/usr/bin/env python3
import subprocess, os, time

os.chdir(r"C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker")

for i in range(10):
    result = subprocess.run(
        ["node", "dist/download-covers.js", "--count", "50"],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    out = result.stdout + result.stderr
    # Write to file to avoid GBK issues
    with open("batch_log.txt", "a", encoding="utf-8") as f:
        f.write(f"\n=== Batch {i} ===\n{out}\n")
    
    # Check if done
    if "0 \u603b\u8ba1" in out or "0 / 0" in out or "/ 0 " in out:
        print(f"Batch {i}: done, no more to download")
        break
    
    # Quick summary
    import re
    m = re.search(r'(\d+) \u6210\u529f', out)
    ok = m.group(1) if m else "?"
    m2 = re.search(r'(\d+) \u5931\u8d25', out)
    fail = m2.group(1) if m2 else "?"
    print(f"Batch {i}: ok={ok} fail={fail}")

# Final count
cov = "covers"
print(f"Total covers: {len(os.listdir(cov)) if os.path.exists(cov) else 0}")
