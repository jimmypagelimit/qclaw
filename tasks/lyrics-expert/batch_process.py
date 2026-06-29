#!/usr/bin/env python3
"""
L项目 - 批量歌词获取
从 unprocessed_albums.txt 读取待处理专辑，批量运行 lyrics_pipeline.py
"""
import os
import sys
import time
import subprocess

LYRICS_PIPELINE = os.path.join(os.path.dirname(__file__), 'lyrics_pipeline.py')
UNPROCESSED_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'unprocessed_albums.txt')

def parse_unprocessed(file_path):
    """解析未处理专辑列表"""
    albums = []
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('未处理') or line.startswith('='):
            continue
        # 格式: "1. 艺人 - 专辑"
        if '. ' in line:
            parts = line.split('. ', 1)[1]  # 去掉序号
            if ' - ' in parts:
                artist, album = parts.split(' - ', 1)
                albums.append((artist.strip(), album.strip()))
    
    return albums

def process_batch(albums, batch_size=5, delay=10):
    """
    批量处理专辑
    batch_size: 每批处理数量
    delay: 专辑间延迟（秒）
    """
    total = len(albums)
    print(f"\n{'='*60}")
    print(f"批量处理开始: 共 {total} 张专辑")
    print(f"批次大小: {batch_size}, 延迟: {delay}s")
    print(f"{'='*60}\n")
    
    results = {
        'success': [],
        'failed': [],
        'skipped': []
    }
    
    for i, (artist, album) in enumerate(albums, 1):
        print(f"\n[{i}/{total}] 处理: {artist} - {album}")
        print(f"{'-'*60}")
        
        try:
            # 调用 lyrics_pipeline.py
            cmd = [sys.executable, LYRICS_PIPELINE, artist, album]
            print(f"CMD: {' '.join(cmd)}")
            
            result = subprocess.run(
                cmd,
                cwd=os.path.dirname(LYRICS_PIPELINE),
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0:
                print(f"[OK] 成功: {artist} - {album}")
                results['success'].append((artist, album))
            else:
                print(f"[X] 失败: {artist} - {album}")
                print(f"STDERR: {result.stderr[-500:] if result.stderr else 'N/A'}")
                results['failed'].append((artist, album, result.returncode))
            
        except subprocess.TimeoutExpired:
            print(f"[X] 超时: {artist} - {album}")
            results['failed'].append((artist, album, 'timeout'))
        except Exception as e:
            print(f"[X] 异常: {e}")
            results['failed'].append((artist, album, str(e)))
        
        # 延迟（避免被MB/LRCLIB限流）
        if i < total:
            print(f"\n等待 {delay} 秒...")
            time.sleep(delay)
    
    # 汇总
    print(f"\n{'='*60}")
    print(f"批量处理完成")
    print(f"{'='*60}")
    print(f"成功: {len(results['success'])}")
    print(f"失败: {len(results['failed'])}")
    print(f"跳过: {len(results['skipped'])}")
    
    # 保存结果
    result_file = os.path.join(os.path.dirname(UNPROCESSED_FILE), 'batch_result.txt')
    with open(result_file, 'w', encoding='utf-8') as f:
        f.write(f"批量处理报告\n")
        f.write(f"{'='*60}\n\n")
        f.write(f"成功: {len(results['success'])}\n")
        for a, b in results['success']:
            f.write(f"  [OK] {a} - {b}\n")
        f.write(f"\n失败: {len(results['failed'])}\n")
        for a, b, c in results['failed']:
            f.write(f"  [X] {a} - {b} (reason={c})\n")
    
    print(f"\n[OK] 报告已保存: {result_file}")
    return results

if __name__ == '__main__':
    # 读取未处理列表
    if not os.path.exists(UNPROCESSED_FILE):
        print(f"[X] 未找到: {UNPROCESSED_FILE}")
        sys.exit(1)
    
    albums = parse_unprocessed(UNPROCESSED_FILE)
    print(f"[OK] 解析到 {len(albums)} 张待处理专辑")
    
    # 处理前10张（测试）
    batch = albums[:10]
    print(f"\n开始处理前 {len(batch)} 张专辑...\n")
    process_batch(batch, batch_size=1, delay=15)
