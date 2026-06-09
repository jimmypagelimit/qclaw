# Album Tracker 修复记录

## 时间
2026-06-09 04:32 (Asia/Shanghai)

## 问题诊断

### 错误1: PowerShell 语法错误
- **现象**: `&&` 操作符解析错误（Windows PowerShell 5.1 不支持 `&&`）
- **位置**: HEARTBEAT.md 中的 album-tracker 脚本配置
- **原因**: `&&` 是 CMD/bash 语法，PowerShell 用 `;` 或 `Start-Process`

### 错误2: 数据库路径错误
- **现象**: `ENOENT: no such file or directory, open 'G:\原创计划\music'`
- **位置**: `dist/download-covers.js` 第59行
- **原因**: 硬编码了不存在的 G 盘路径

### 错误3: 数据库文件为空
- **现象**: `Error: file is not a database`
- **原因**: `_music_latest.db` 文件大小为 0 字节，未初始化

## 修复步骤

### 1. 修复 PowerShell 语法
**文件**: `HEARTBEAT.md`
```diff
- cd {workspace_root_dir}\tasks\2026-05-12-long-term-project\album-tracker && node dist/download-covers.js --count 10
+ cd C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker; node dist/download-covers.js --count 10
```

### 2. 修复数据库路径
**文件**: `dist/download-covers.js` 第59行
```diff
- const DB_PATH = 'G:/原创计划/music';
+ const DB_PATH = path.join(__dirname, '..', '_music_latest.db');
```

### 3. 初始化数据库
**创建脚本**: `scripts/init-db.js`
- 从 `database.sql` 读取 SQL 语句
- 使用 sql.js 执行 SQL 创建数据库表结构
- 导出为 `_music_latest.db` 文件

**执行结果**:
```
SQL 文件大小: 493950 字节
数据库已写入: _music_latest.db 大小: 499712 字节
数据库表: albums, albums_2024, albums_2025, albums_2026, artists, genres, ...
```

### 4. 验证修复
**测试命令**:
```powershell
cd C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker; node dist/download-covers.js --count 2
```

**测试结果**:
```
🔍 找到 2 张需要封面的专辑（offset=0, count=2）

[01] 郑钧=zj - 郑钧 ... ❌ 所有源均未找到
[02] Is It Gonna Happen Again? - jody积融 ... ✅ (netease, 25163B)

💾 数据库已保存
📊 结果: ✅ 1 成功 / ❌ 1 失败 / 📋 2 总计
```

## 关键发现

1. **album-tracker 目录结构**:
   - `database.sql` - SQL 文本转储文件（493KB）
   - `_music_latest.db` - 二进制 SQLite 数据库文件（应 ≥ 499KB）
   - `covers/` - 已下载封面目录（510 个文件）
   - `dist/download-covers.js` - 封面下载脚本

2. **sql.js 正确用法**:
   ```javascript
   const sql = require("sql.js");
   sql.default({ locateFile: ... }).then(SQL => {
     const db = new SQL.Database();
     // ...
   });
   ```

3. **PowerShell 语法**:
   - ❌ 不支持 `&&`（CMD/bash 语法）
   - ✅ 使用 `;` 分隔命令
   - ✅ 使用 `Start-Process` 启动进程

## 后续建议

1. ** Heartbeat 自动化**: 修复后 `download-covers.js` 可以正常执行，heartbeat 可以重新启用专辑封面下载任务

2. **路径配置化**: 考虑将数据库路径写入配置文件（如 `config.json`），避免硬编码

3. **G 盘依赖**: 原脚本依赖 G 盘（`G:\原创计划\music`），需要确认：
   - G 盘是否是外部硬盘？
   - 是否需要同步回 G 盘？
   - 当前改为本地 `_music_latest.db`，是否影响其他功能？

4. **数据库同步**: 如果 G 盘是主数据源，需要建立同步机制：
   - 启动时从 G 盘同步到本地
   - 或改用网络路径 `\\server\share\music.db`

## 测试清单

- [x] PowerShell 语法修复
- [x] 数据库路径修复
- [x] 数据库初始化
- [x] 下载脚本测试（--count 2）
- [ ] 完整下载测试（--count 10）
- [ ] Heartbeat 自动化测试
- [ ] G 盘同步机制确认

## 文件变更

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| `HEARTBEAT.md` | 修改 | 修复 PowerShell 语法 |
| `dist/download-covers.js` | 修改 | 修复数据库路径 |
| `scripts/init-db.js` | 新增 | 数据库初始化脚本 |
| `_music_latest.db` | 重建 | 从 SQL 文件初始化（499KB）|

## 结论

成功修复 album-tracker 的三个关键问题，下载脚本现在可以正常运行。建议后续：
1. 确认 G 盘的作用和同步需求
2. 将配置项（如数据库路径）外部化
3. 在 heartbeat 中重新启用自动下载任务
