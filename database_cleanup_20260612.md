# 数据库清理 - 2026-06-12

## 目标
删除所有重复的数据库文件，只保留唯一正确的数据库：`C:\Users\qujt\.qclaw\workspace\_music_latest.db`

## 问题背景
之前多次误操作导致数据库文件路径混乱：
- `workspace/_music_latest.db` - Web 服务实际使用的正确数据库
- `album-tracker/_music_latest.db` - 副本，导致数据不同步
- 多个临时数据库文件（`_music_fill*.db`, `_music_fix_*.db` 等）

用户要求："删掉其他库，只保留一个，万万别再找错了"

## 执行步骤

### 1. 停止 Web 服务
```
taskkill /F /IM node.exe
```

### 2. 查找所有数据库文件
使用 Python 脚本 `_cleanup_databases.py` 查找所有 `_music*.db` 文件：
- 找到 3 个文件（其中2个是同一文件的重复计数）
- 1 个需要删除：`album-tracker/_music_latest.db`

### 3. 删除重复文件
删除：`C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\_music_latest.db`

### 4. 验证结果
验证后只剩一个文件：
```
C:/Users/qujt/.qclaw/workspace/_music_latest.db
```

### 5. 重启 Web 服务
```
node dist/server.js (in album-tracker directory)
```

## 结果

✅ **成功**：现在只有一个数据库文件

- 路径：`C:\Users\qujt\.qclaw\workspace\_music_latest.db`
- 大小：0.6 MB
- 内容：519 张专辑，1044 条收听记录

## 后续规则

1. **永远只操作这个路径的数据库文件**
2. **改库前必须停 Web 服务**
3. **操作后立即验证**
4. **完成后重启 Web 服务**
5. **TOOLS.md 已更新路径规则**

## 清理的临时文件清单

之前已清理 85 个临时文件（2026-06-12 20:00）：
- `_music.db`, `_music_add.db`, `_music_fill*.db` (10个)
- `_music_fix_dur*.db` (10个)
- `_music_fix_fmt.db`, `_music_fix_ry.db`
- `_music_latest_backup_20260607.db`
- `_music_phase1*.db` (5个)

本次清理：
- `album-tracker/_music_latest.db` (副本)

## 验证命令

```python
import glob
files = glob.glob('C:/Users/qujt/.qclaw/workspace/**/_music*.db', recursive=True)
print(f'Total DB files: {len(files)}')
for f in files:
    print(f)
```

---

**重要**：以后所有数据库操作必须用这个唯一文件，不能再有副本！
