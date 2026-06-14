#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用 opencli 连接已有 Chrome，访问 RYM piano rock 页面提取定义
"""

import subprocess
import time
import json
import re
import os

def run_opencli(args, timeout=30):
    cmd = ["opencli", "browser", "work"] + args
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, 
                          encoding='utf-8', errors='replace')
    return result.stdout + result.stderr

def main():
    # 1. Bind to existing Chrome
    print("[1] Binding to Chrome...")
    out = run_opencli(["bind"])
    print(f"  bind: {out.strip()[:200]}")
    
    # 2. Open RYM genre page
    print("[2] Opening RYM piano rock page...")
    out = run_opencli(["open", "https://rateyourmusic.com/genre/piano+rock/"])
    print(f"  open: {out.strip()[:200]}")
    
    # 3. Wait for CF challenge
    print("[3] Waiting 30s for CF challenge...")
    time.sleep(30)
    
    # 4. Extract page content
    print("[4] Extracting content...")
    out = run_opencli(["extract"], timeout=60)
    
    # Save raw output
    with open(r'C:\Users\qujt\.qclaw\workspace\tasks\rym-expert\_tmp_piano_rock_opencli.md', 'w', encoding='utf-8') as f:
        f.write(out)
    
    print(f"  Extracted {len(out)} chars")
    print(f"  Preview: {out[:500]}...")
    
    # 5. Close session
    run_opencli(["close"])
    print("[5] Done")

if __name__ == "__main__":
    main()
