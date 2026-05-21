#!/usr/bin/env python3
"""
读取 SQLite 数据库表结构
用法: python read_sqlite_schema.py <database_path>
"""

import sqlite3
import sys

def read_schema(db_path):
    """读取 SQLite 数据库的表结构"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"📊 数据库: {db_path}")
        print(f"📋 找到 {len(tables)} 个表\n")
        
        for (table_name,) in tables:
            print(f"{'='*60}")
            print(f"表: {table_name}")
            print('='*60)
            
            # 获取表结构
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            print(f"\n字段 ({len(columns)} 个):")
            print(f"{'ID':<5} {'名称':<20} {'类型':<15} {'非空':<5} {'默认值':<15} {'主键':<5}")
            print('-'*70)
            
            for col in columns:
                cid, name, dtype, notnull, dflt_value, pk = col
                notnull_str = "YES" if notnull else "NO"
                pk_str = "YES" if pk else "NO"
                print(f"{cid:<5} {name:<20} {dtype:<15} {notnull_str:<5} {str(dflt_value):<15} {pk_str:<5}")
            
            # 获取样例数据（前3行）
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
            rows = cursor.fetchall()
            
            if rows:
                print(f"\n样例数据 (前3行):")
                for row in rows:
                    print(f"  {row}")
            
            # 获取记录总数
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"\n总记录数: {count}\n")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ 数据库错误: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("用法: python read_sqlite_schema.py <database_path>")
        sys.exit(1)
    
    db_path = sys.argv[1]
    read_schema(db_path)
