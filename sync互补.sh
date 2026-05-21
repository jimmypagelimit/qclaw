#!/bin/bash

# 增量同步脚本 - 互相补充模式
# 源目录和目标目录互相补充，确保两边都有完整的文件

SOURCE="$(pwd)"
TARGET="C:/荒岛唱片"
LOG_FILE="$SOURCE/SyncLog.txt"

echo "$(date '+%Y-%m-%d %H:%M:%S') - 开始同步（互相补充模式）" > "$LOG_FILE"

# 从 SOURCE 同步到 TARGET（新增和修改）
find "$SOURCE" -type f -not -path "*/.git/*" -not -name "SyncLog.txt" -not -name "sync.sh" -not -name "sync.bat" | while read file; do
    relative_path="${file#$SOURCE/}"
    target_file="$TARGET/$relative_path"
    target_dir="$(dirname "$target_file")"
    
    if [ ! -d "$target_dir" ]; then
        mkdir -p "$target_dir"
    fi
    
    if [ ! -f "$target_file" ] || [ "$file" -nt "$target_file" ]; then
        cp -f "$file" "$target_file"
        echo "同步到C盘: $relative_path" >> "$LOG_FILE"
    fi
done

# 从 TARGET 同步到 SOURCE（补充 SOURCE 没有的文件）
find "$TARGET" -type f -not -path "*/.git/*" -not -name "SyncLog.txt" -not -name "sync.sh" -not -name "sync.bat" | while read file; do
    relative_path="${file#$TARGET/}"
    source_file="$SOURCE/$relative_path"
    source_dir="$(dirname "$source_file")"
    
    if [ ! -d "$source_dir" ]; then
        mkdir -p "$source_dir"
    fi
    
    if [ ! -f "$source_file" ] || [ "$file" -nt "$source_file" ]; then
        cp -f "$file" "$source_file"
        echo "同步到H盘: $relative_path" >> "$LOG_FILE"
    fi
done

echo "$(date '+%Y-%m-%d %H:%M:%S') - 同步完成" >> "$LOG_FILE"
echo "同步完成！"
