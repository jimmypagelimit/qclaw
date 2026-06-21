#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pf_batch_fill_v2.py - Batch fill Pitchfork scores (resume-safe)

Improvements over v1:
    - Saves progress after each album (resume if killed)
    - Processes in configurable batch sizes
    - Skips already-processed albums (checks DB before querying PF)
    - Better error handling

Usage:
    C:\Python311\python.exe pf_batch_fill_v2.py          # Process all
    C:\Python311\python.exe pf_batch_fill_v2.py --limit 50
    C:\Python311\python.exe pf_batch_fill_v2.py --resume  # Skip already-tried albums
"""

import sys
import os
import sqlite3
import time
import json
import subprocess
import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pf_query import query_album

DB_PATH = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
WEB_SERVICE_PORT = 3456
LOG_FILE = os.path.join(os.path.dirname(__file__), 'pf_batch_fill.log')
PROGRESS_FILE = os.path.join(os.path.dirname(__file__), 'pf_batch_progress.json')

def log(msg):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {msg}"
    # Windows console may not support all Unicode characters
    try:
        print(line)
    except UnicodeEncodeError:
        # Fallback: encode with replacement characters
        safe_line = line.encode('gbk', errors='replace').decode('gbk')
        print(safe_line)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + '\n')

def load_progress():
    """Load processed album IDs from progress file."""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return set(json.load(f))
    return set()

def save_progress(processed_ids):
    """Save processed album IDs to progress file."""
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(list(processed_ids), f)

def stop_web_service():
    log("Stopping web service...")
    try:
        result = subprocess.run(
            f'netstat -ano | findstr :{WEB_SERVICE_PORT}',
            shell=True, capture_output=True, text=True
        )
        if result.stdout:
            for line in result.stdout.strip().split('\n'):
                if 'LISTENING' in line:
                    pid = line.strip().split()[-1]
                    log(f"Killing process {pid}")
                    subprocess.run(f'taskkill /PID {pid} /F', shell=True, capture_output=True)
                    time.sleep(2)
                    log("Web service stopped")
                    return True
        log("No web service found running")
        return True
    except Exception as e:
        log(f"Error stopping web service: {e}")
        return False

def start_web_service():
    log("Starting web service...")
    try:
        result = subprocess.run(
            f'netstat -ano | findstr :{WEB_SERVICE_PORT}',
            shell=True, capture_output=True, text=True
        )
        if result.stdout and 'LISTENING' in result.stdout:
            log("Web service already running")
            return True
        
        web_dir = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker'
        subprocess.Popen(
            f'start "" "node" "dist/server.js"',
            shell=True, cwd=web_dir
        )
        time.sleep(3)
        log("Web service started")
        return True
    except Exception as e:
        log(f"Error starting web service: {e}")
        return False

def get_albums_to_process(limit=None, resume=False):
    """Get Western albums missing PF score."""
    processed = load_progress() if resume else set()
    
    # Load Western albums list
    western_file = os.path.join(os.path.dirname(__file__), 'pf_western_albums.json')
    if os.path.exists(western_file):
        with open(western_file, 'r', encoding='utf-8') as f:
            western_data = json.load(f)
            western_ids = {item['id'] for item in western_data}
    else:
        western_ids = None  # No filter if file not found
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    if western_ids:
        # Only process Western albums
        placeholders = ','.join(['?'] * len(western_ids))
        query = f"""
            SELECT album_id, album_name, artist 
            FROM albums 
            WHERE pitchfork_score IS NULL 
            AND album_id IN ({placeholders})
            ORDER BY album_id
        """
        c.execute(query, list(western_ids))
    else:
        # Fallback: process all
        query = """
            SELECT album_id, album_name, artist 
            FROM albums 
            WHERE pitchfork_score IS NULL 
            ORDER BY album_id
        """
        c.execute(query)
    
    rows = c.fetchall()
    conn.close()
    
    # Filter out already-processed (if resume mode)
    if resume and processed:
        rows = [r for r in rows if r[0] not in processed]
        log(f"Resume mode: skipping {len(processed)} already-processed albums")
    
    if limit:
        rows = rows[:limit]
    
    log(f"Found {len(rows)} Western albums to process")
    return rows, processed

def update_album(conn, album_id, score, review_url):
    c = conn.cursor()
    try:
        c.execute(
            "UPDATE albums SET pitchfork_score = ?, review_url = ? WHERE album_id = ?",
            (score, review_url, album_id)
        )
        conn.commit()
        return True
    except Exception as e:
        log(f"Error updating album {album_id}: {e}")
        return False

def main():
    dry_run = '--dry-run' in sys.argv
    limit = None
    resume = '--resume' in sys.argv
    
    for i, arg in enumerate(sys.argv):
        if arg == '--limit' and i + 1 < len(sys.argv):
            try:
                limit = int(sys.argv[i + 1])
            except ValueError:
                pass
    
    if dry_run:
        log("=== DRY RUN MODE (no DB updates) ===")
    
    log("=== Pitchfork Batch Fill v2 Started ===")
    
    # Stop web service
    if not dry_run:
        if not stop_web_service():
            log("ERROR: Could not stop web service. Aborting.")
            return
    
    # Get albums to process
    albums, processed_ids = get_albums_to_process(limit=limit, resume=resume)
    
    if not albums:
        log("No albums to process. Exiting.")
        if not dry_run:
            start_web_service()
        return
    
    # Process
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    
    success_count = 0
    not_found_count = 0
    error_count = 0
    
    try:
        for idx, (album_id, album_name, artist) in enumerate(albums, 1):
            log(f"[{idx}/{len(albums)}] Processing: {artist} - {album_name}")
            
            try:
                result = query_album(artist, album_name)
                
                if result['found'] and result['score'] is not None:
                    score = result['score']
                    review_url = result['review_url']
                    
                    log(f"  Found: score={score}, URL={review_url}")
                    
                    if not dry_run:
                        if update_album(conn, album_id, score, review_url):
                            success_count += 1
                    else:
                        success_count += 1
                else:
                    log(f"  Not found: {result.get('error', 'Unknown')}")
                    not_found_count += 1
                
                # Save progress
                processed_ids.add(album_id)
                if idx % 5 == 0:  # Save every 5 albums
                    save_progress(processed_ids)
                
                # Rate limit
                if idx < len(albums):
                    time.sleep(1.5)
                    
            except Exception as e:
                log(f"  Error: {e}")
                error_count += 1
                time.sleep(3)
        
        # Final progress save
        save_progress(processed_ids)
        
    finally:
        conn.close()
        
        # Restart web service
        if not dry_run:
            start_web_service()
    
    # Summary
    log("=== Pitchfork Batch Fill v2 Completed ===")
    log(f"Total processed: {len(albums)}")
    log(f"Success: {success_count}")
    log(f"Not found: {not_found_count}")
    log(f"Errors: {error_count}")
    log(f"Progress saved to: {PROGRESS_FILE}")
    log(f"Log file: {LOG_FILE}")

if __name__ == '__main__':
    main()
