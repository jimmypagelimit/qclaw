#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动修复专辑封面：清除无效 cover_image_url，重新下载
"""
import sqlite3
import os
import subprocess
import time

DB_PATH = r"G:\原创计划\music"
COVERS_DIR = r"C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\covers"
PROJECT_DIR = r"C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker"

def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 1. 查找所有 cover_image_url 非空的专辑
    c.execute("SELECT album_id, cover_image_url FROM albums WHERE cover_image_url IS NOT NULL AND cover_image_url != ''")
    rows = c.fetchall()
    print(f"数据库中 cover_image_url 非空的专辑数: {len(rows)}")

    # 2. 检查文件是否真的存在
    missing_ids = []
    for album_id, cover_url in rows:
        if cover_url.startswith("/covers/"):
            filename = cover_url.replace("/covers/", "", 1)
        else:
            filename = os.path.basename(cover_url)
        filepath = os.path.join(COVERS_DIR, filename)
        if not os.path.exists(filepath):
            missing_ids.append(album_id)

    print(f"文件缺失的专辑数: {len(missing_ids)}")

    if not missing_ids:
        print("✅ 所有封面文件都存在，无需修复")
        conn.close()
        return

    # 3. 清除这些记录的 cover_image_url
    placeholders = ','.join(['?'] * len(missing_ids))
    c.execute(f"UPDATE albums SET cover_image_url = NULL WHERE album_id IN ({placeholders})", missing_ids)

    # 同时清除年份表中的记录
    for year_table in ['albums_2024', 'albums_2025', 'albums_2026']:
        try:
            c.execute(f"UPDATE {year_table} SET cover_image_url = NULL WHERE album_id IN ({placeholders})", missing_ids)
        except:
            pass  # 表可能不存在

    conn.commit()
    print(f"✅ 已清除 {len(missing_ids)} 条记录的 cover_image_url")

    # 4. 重新下载封面（需要先确保服务器已停）
    print("\n开始重新下载封面...")
    os.chdir(PROJECT_DIR)
    result = subprocess.run(
        ["node", "dist/download-covers.js", "--count", "20"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    print("下载输出:", result.stdout[:2000])
    if result.stderr:
        print("错误:", result.stderr[:1000])

    # 5. 检查下载结果
    if os.path.exists(COVERS_DIR):
        files = os.listdir(COVERS_DIR)
        print(f"\n✅ 封面目录文件数: {len(files)}")
        if files:
            print("示例文件:", files[:3])

    conn.close()

    # 6. 重启服务器
    print("\n重启 Web 服务器...")
    env = os.environ.copy()
    env["SQLITE_PATH"] = DB_PATH
    subprocess.Popen(
        ["node", "dist/server.js"],
        env=env,
        cwd=PROJECT_DIR,
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    time.sleep(3)
    print("✅ 服务器已重启，等待封面加载...")

if __name__ == "__main__":
    main()
