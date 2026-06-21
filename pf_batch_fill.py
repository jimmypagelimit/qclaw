#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pf_batch_fill.py - Batch fill Pitchfork scores + review URLs for albums

Usage:
    C:\Python311\python.exe pf_batch_fill.py          # Process all albums missing PF score
    C:\Python311\python.exe pf_batch_fill.py --dry-run  # Test mode, don't update DB
    C:\Python311\python.exe pf_batch_fill.py --limit 50  # Process only 50 albums

Notes:
    - Stops web service before DB access, restarts after
    - Rate limits to 1.5s between requests
    - Can resume if interrupted (checks DB for existing values)
    - Logs all actions to pf_batch_fill.log
"""

import sys
import os
import sqlite3
import time
import json
import subprocess
import signal

# Add workspace to path so we can import pf_query
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pf_query import query_album

DB_PATH = r'C:\Users\qujt\.qclaw\workspace\_music_latest.db'
WEB_SERVICE_PORT = 3456
LOG_FILE = os.path.join(os.path.dirname(__file__), 'pf_batch_fill.log')

def log(msg):
    """Log to both console and file."""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    line = f"[{timestamp}] {msg}"
    print(line)
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(line + '\n')

def stop_web_service():
    """Stop the album-tracker web service (port 3456)."""
    log("Stopping web service...")
    try:
        # Find process using port 3456
        result = subprocess.run(
            f'netstat -ano | findstr :{WEB_SERVICE_PORT}',
            shell=True, capture_output=True, text=True
        )
        if result.stdout:
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if 'LISTENING' in line:
                    pid = line.strip().split()[-1]
                    log(f"Killing process {pid} on port {WEB_SERVICE_PORT}")
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
    """Start the album-tracker web service."""
    log("Starting web service...")
    try:
        # Check if already running
        result = subprocess.run(
            f'netstat -ano | findstr :{WEB_SERVICE_PORT}',
            shell=True, capture_output=True, text=True
        )
        if result.stdout and 'LISTENING' in result.stdout:
            log("Web service already running")
            return True
        
        # Start service
        web_dir = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker'
        node_exe = 'node'
        server_js = os.path.join(web_dir, 'dist', 'server.js')
        
        # Start in background
        subprocess.Popen(
            f'start "" "{node_exe}" "{server_js}"',
            shell=True, cwd=web_dir
        )
        time.sleep(3)
        log("Web service started")
        return True
    except Exception as e:
        log(f"Error starting web service: {e}")
        return False

def get_albums_to_process(limit=None, dry_run=False):
    """Get albums from DB that are missing Pitchfork score."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    query = """
        SELECT album_id, album_name, artist 
        FROM albums 
        WHERE pitchfork_score IS NULL 
        ORDER BY album_id
    """
    if limit:
        query += f" LIMIT {limit}"
    
    c.execute(query)
    rows = c.fetchall()
    conn.close()
    
    log(f"Found {len(rows)} albums missing Pitchfork score")
    return rows

def update_album(conn, album_id, score, review_url, bnm=None):
    """Update album with Pitchfork data."""
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
    
    for i, arg in enumerate(sys.argv):
        if arg == '--limit' and i + 1 < len(sys.argv):
            try:
                limit = int(sys.argv[i + 1])
            except ValueError:
                pass
    
    if dry_run:
        log("=== DRY RUN MODE (no DB updates) ===")
    
    log("=== Pitchfork Batch Fill Started ===")
    
    # Step 1: Stop web service
    if not dry_run:
        if not stop_web_service():
            log("ERROR: Could not stop web service. Aborting.")
            return
    
    # Step 2: Get albums to process
    albums = get_albums_to_process(limit=limit)
    
    if not albums:
        log("No albums to process. Exiting.")
        if not dry_run:
            start_web_service()
        return
    
    # Step 3: Process each album
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    
    success_count = 0
    not_found_count = 0
    error_count = 0
    
    for idx, (album_id, album_name, artist) in enumerate(albums, 1):
        log(f"[{idx}/{len(albums)}] Processing: {artist} - {album_name}")
        
        try:
            result = query_album(artist, album_name)
            
            if result['found'] and result['score'] is not None:
                score = result['score']
                review_url = result['review_url']
                bnm = result.get('bnm')
                
                log(f"  Found: score={score}, BNM={bnm}, URL={review_url}")
                
                if not dry_run:
                    if update_album(conn, album_id, score, review_url, bnm):
                        success_count += 1
                    else:
                        error_count += 1
                else:
                    success_count += 1
            else:
                log(f"  Not found: {result.get('error', 'Unknown error')}")
                not_found_count += 1
            
            # Rate limiting
            if idx < len(albums):
                time.sleep(1.5)
                
        except Exception as e:
            log(f"  Error: {e}")
            error_count += 1
            time.sleep(3)
    
    conn.close()
    
    # Step 4: Restart web service
    if not dry_run:
        start_web_service()
    
    # Summary
    log("=== Pitchfork Batch Fill Completed ===")
    log(f"Total processed: {len(albums)}")
    log(f"Success: {success_count}")
    log(f"Not found: {not_found_count}")
    log(f"Errors: {error_count}")
    log(f"Log file: {LOG_FILE}")

if __name__ == '__main__':
    main()
