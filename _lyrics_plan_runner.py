# -*- coding: utf-8 -*-
"""
歌词计划自动运行脚本 - 读取状态并推进批次
用法：python _lyrics_plan_runner.py
定时任务将运行此脚本
"""

import os
import re
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

STATE_FILE = r'C:\Users\qujt\.qclaw\workspace\_lyrics_batch_state.txt'
BATCH_SCRIPT = r'C:\Users\qujt\.qclaw\workspace\_lyrics_batch_comprehensive.py'

def read_state():
    """读取状态文件"""
    state = {
        'current_batch': 1,
        'batch_size': 100,
        'total_tracks': 4988,
        'last_update': ''
    }
    
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
            for line in content.split('\n'):
                if line.startswith('current_batch:'):
                    state['current_batch'] = int(line.split(':')[1].strip())
                elif line.startswith('batch_size:'):
                    state['batch_size'] = int(line.split(':')[1].strip())
                elif line.startswith('total_tracks:'):
                    state['total_tracks'] = int(line.split(':')[1].strip())
                elif line.startswith('last_update:'):
                    state['last_update'] = line.split(':', 1)[1].strip()
    
    return state

def write_state(state):
    """写入状态文件"""
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        f.write('# 歌词计划批次状态\n')
        f.write('# 自动管理，勿手动编辑\n\n')
        f.write(f"current_batch: {state['current_batch']}\n")
        f.write(f"batch_size: {state['batch_size']}\n")
        f.write(f"total_tracks: {state['total_tracks']}\n")
        f.write(f"last_update: {state['last_update']}\n")

def run_batch(batch_num):
    """运行指定批次"""
    import subprocess
    import datetime
    
    print(f"Running batch {batch_num}...")
    
    result = subprocess.run(
        ['C:\\Python311\\python.exe', BATCH_SCRIPT, str(batch_num)],
        capture_output=True,
        encoding='utf-8',
        errors='replace'
    )
    
    print(result.stdout)
    if result.stderr:
        print("Errors:")
        print(result.stderr)
    
    # 更新状态
    state = read_state()
    state['current_batch'] = batch_num + 1
    state['last_update'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    write_state(state)
    
    print(f"Batch {batch_num} done. Next batch: {state['current_batch']}")

def main():
    state = read_state()
    current_batch = state['current_batch']
    
    print(f"Lyrics plan runner started.")
    print(f"Current batch: {current_batch}")
    print(f"Batch size: {state['batch_size']}")
    
    # 运行当前批次
    run_batch(current_batch)

if __name__ == '__main__':
    main()
