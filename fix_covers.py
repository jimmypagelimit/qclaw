#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复专辑封面：清理数据库中无效 cover_image_url（文件不存在的记录），然后重新下载
"""
import sqlite3
import os
import subprocess
import time

DB_PATH = r"G:\原创计划\music\music"
COVERS_DIR = r"C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\covers"

def main():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 1. 查找所有 cover_image_url 非空的专辑
    c.execute("SELECT album_id, cover_image_url FROM albums WHERE cover_image_url IS NOT NULL AND cover_image_url != ''")
    rows = c.fetchall()
    print(f"数据库中 cover_image_url 非空的专辑数: {len(rows)}")

    # 2. 检查文件是否真的存在
    missing = []
    for album_id, cover_url in rows:
        # cover_image_url 格式 like "/covers/323-COV.jpg"
        if cover_url.startswith("/covers/"):
            filename = cover_url.replace("/covers/", "", 1)
        else:
            filename = os.path.basename(cover_url)
        filepath = os.path.join(COVERS_DIR, filename)
        if not os.path.exists(filepath):
            missing.append((album_id, filename))

    print(f"文件缺失的专辑数: {len(missing)}")
    if missing:
        print("示例缺失:", missing[:5])

        # 3. 清除这些记录的 cover_image_url，触发重新下载
        confirm = input("是否清除这些记录的 cover_image_url 并重新下载？(y/n): ")
        if confirm.lower() == 'y':
            ids = [m[0] for m in missing]
            c.execute(f"UPDATE albums SET cover_image_url = NULL WHERE album_id IN ({','.join(['?']*len(ids))})", ids)
            # 同时清除年份表中的记录
            for year_table in ['albums_2024', 'albums_2025', 'albums_2026']:
                c.execute(f"UPDATE {year_table} SET cover_image_url = NULL WHERE album_id IN ({','.join(['?']*len(ids))})", ids)
            conn.commit()
            print(f"✅ 已清除 {len(missing)} 条记录的 cover_image_url")

            # 4. 重新下载（需要先停服务器，但我们已经停了）
            print("\n开始重新下载封面...")
            os.chdir(os.path.dirname(COVERS_DIR))
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
        else:
            print("取消操作")

    conn.close()

    # 5. 重启服务器
    print("\n重启 Web 服务器...")
    env = os.environ.copy()
    env["SQLITE_PATH"] = DB_PATH
    subprocess.Popen(
        ["node", "dist/server.js"],
        env=env,
        cwd=os.path.dirname(COVERS_DIR),
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    print("完成!")

if __name__ == "__main__":
    main()
