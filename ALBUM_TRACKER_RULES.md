# ALBUM_TRACKER_RULES.md - album-tracker 操作手册

> **核心目标**：每次操作都更准、更快、更少犯错
> **使用方法**：每次操作 album-tracker 前，先读 MEMORY.md 概览，再读本手册获取操作细节

---

## 📋 标准操作流程（SOP）

### 新增专辑完整流程（8步）

**每次用户说"听了一张专辑"或"新增专辑"时，必须执行完整流程：**

1. ✅ **停止 Web 服务**（避免 sql.js 内存冲突）
   ```bash
   tasklist | findstr node
   taskkill /PID <pid> /F
   ```

2. ✅ **写入数据库**（双表同步）
   - 判重：`SELECT id FROM albums WHERE album_name=? AND artist=?`
   - 不存在 → 插入 `albums` + `albums_YYYY`
   - 已存在 → 只增加 `total_listen_count`

3. ✅ **繁简转换**（繁体入库必须先转简体）
   - 运行 `_convert_traditional_v2.py`
   - 人工核对含`著`的记录（ID 539）

4. ✅ **下载封面**（iTunes > Deezer > 网易云）
   - 命名：`{id}-{artist}-{album}.jpg`（空格→下划线）
   - 保存：`\\10.0.2.4\qemu\原创计划\covers\`

5. ✅ **复制封面到 Web 路径**
   - 源：`\\10.0.2.4\qemu\原创计划\covers\`
   - 目标：`album-tracker/public/covers/`
   - Python：`shutil.copy(src, dst)`

6. ✅ **更新数据库 `cover_image_url` 字段**
   ```sql
   UPDATE albums SET cover_image_url = '/covers/{filename}.jpg' WHERE album_id = ?
   UPDATE albums_YYYY SET cover_image_url = '/covers/{filename}.jpg' WHERE album_id = ?
   ```

7. ✅ **导出 `database.sql`**
   ```python
   import sqlite3
   conn = sqlite3.connect(r'\\10.0.2.4\qemu\原创计划\music')
   with open(r'\\10.0.2.4\qemu\原创计划\database.sql', 'w', encoding='utf-8') as f:
       for line in conn.iterdump():
           f.write(line + '\n')
   ```

8. ✅ **Git 提交 + 推送**
   ```bash
   cd C:\Users\qujt\.qclaw\workspace
   cmd /c "C:\Progra~1\Git\bin\bash.exe -l git_add_commit_push.sh"
   ```

9. ✅ **重启 Web 服务**
   ```bash
   cmd /c "cd C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker && start \"\" node dist/server.js"
   ```

10. ✅ **验证**
    - 访问 `http://localhost:3456/api/stats`
    - 确认 HTTP 200
    - 确认封面显示正常

---

## ⚠️ 常见错误与解决方案

### 错误1：封面不匹配（cover_image_url 为 None）

**症状**：
- Web 界面显示专辑但封面缺失
- 浏览器控制台显示 404 错误

**根因**：
1. 封面文件存在备份路径（`\\10.0.2.4\qemu\原创计划\covers\`）
2. 但数据库 `cover_image_url` 字段为 `None`
3. Web 服务器期望封面在 `album-tracker/public/covers/`

**解决**：
1. 更新数据库 `cover_image_url` 字段
2. 复制封面到 `album-tracker/public/covers/`
3. 重启 Web 服务

**预防**：
- 每次下载封面后，立即执行步骤 5+6

---

### 错误2：封面文件路径错误（404 错误）

**症状**：
- 数据库 `cover_image_url` 已设置
- 但浏览器访问 `http://localhost:3456/covers/xxx.jpg` 返回 404

**根因**：
- 封面文件只放在备份路径（`\\10.0.2.4\qemu\原创计划\covers\`）
- 未复制到 Web 访问路径（`album-tracker/public/covers/`）

**解决**：
```python
import shutil
src = r'\\10.0.2.4\qemu\原创计划\covers\{filename}.jpg'
dst = r'C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker\public\covers\{filename}.jpg'
shutil.copy(src, dst)
```

**预防**：
- 在操作流程中强制要求步骤 5

---

### 错误3：繁简转换遗漏

**症状**：
- 用户反馈"繁体入库的专辑一定要先转为简体"
- 数据库中存在繁体中文专辑名

**根因**：
- 入库时未执行繁简转换
- 自动转换脚本未覆盖所有字符

**解决**：
1. 运行 `_convert_traditional_v2.py`
2. 人工核对含`著`的记录（有歧义）

**预防**：
- 在操作流程中强制要求步骤 3
- 建立无歧义映射表（并→并、於→于、體→体等）
- 标记需人工核对的字符（`著`、`干`）

---

### 错误4：PowerShell 编码问题

**症状**：
- Python 脚本中的 emoji 无法在 GBK 控制台显示
- 报错：`UnicodeEncodeError: 'gbk' codec can't encode character`

**根因**：
- Windows 控制台默认编码 GBK
- emoji（如 ✅）无法用 GBK 编码

**解决**：
1. 移除脚本中的 emoji
2. 改用 `[OK]` `[FAIL]` 等 ASCII 标记
3. 或者：`sys.stdout.reconfigure(encoding='utf-8')`

**预防**：
- 永远别用 PowerShell 执行含中文/emoji 的 Python 命令
- 写脚本文件执行，输出到 UTF-8 文件

---

### 错误5：Git push 超时

**症状**：
- `git push` 命令执行超时
- 报错：`fatal: unable to access 'https://github.com/...': Failed to connect`

**根因**：
- 网络不稳定
- GitHub 服务器响应慢

**解决**：
1. 等待网络恢复后手动推送
2. 或者：增加 git 超时时间
   ```bash
   git config --global http.postBuffer 524288000
   ```

**预防**：
- 在操作流程中，Git 推送步骤设置超时时间（如 60 秒）
- 如果超时，记录待推送 commit，稍后手动推送

---

## 🔧 工具脚本清单

### 1. `_add_album.py` - 新增专辑（待完善）

**功能**：
- 自动执行标准操作流程（8步）
- 内置繁简转换
- 自动下载封面
- 自动更新数据库字段
- 自动 Git 提交推送

**当前状态**：❌ 未完善（需手动执行各步骤）

**待实现**：
- [ ] 自动停止/重启 Web 服务
- [ ] 自动繁简转换
- [ ] 自动下载封面（iTunes > Deezer > 网易云）
- [ ] 自动复制封面到 Web 路径
- [ ] 自动更新数据库字段
- [ ] 自动导出 database.sql
- [ ] 自动 Git 提交推送

---

### 2. `_convert_traditional_v2.py` - 繁简转换 ✅

**功能**：
- 批量转换 albums 表和 albums_YYYY 表中的繁体中文为简体
- 使用无歧义映射表
- 标记需人工核对的记录（含`著`字符）

**使用方法**：
```bash
cmd /c "C:\Python311\python.exe _convert_traditional_v2.py"
```

**映射表**：
- 并→并、於→于、體→体、會→会、後→后、學→学、門→门、國→国
- ⚠️  著→？（需人工核对）

---

### 3. `_download_cover.py` - 下载封面（待完善）

**功能**：
- 根据专辑名和艺术家搜索封面
- 优先级：iTunes API > Deezer API > 网易云 API
- 自动保存到 `\\10.0.2.4\qemu\原创计划\covers\`
- 自动复制到 `album-tracker/public/covers/`

**当前状态**：❌ 未实现（目前手动下载）

**待实现**：
- [ ] iTunes API 搜索
- [ ] Deezer API 搜索
- [ ] 网易云 API 搜索
- [ ] 自动选择最佳质量封面
- [ ] 自动复制 to Web 路径

---

### 4. `_verify_album.py` - 验证专辑数据（待完善）

**功能**：
- 验证专辑数据完整性
- 检查封面文件是否存在
- 检查 `cover_image_url` 字段是否正确
- 检查繁简转换是否完整

**当前状态**：❌ 未实现

**待实现**：
- [ ] 验证 albums 表和 albums_YYYY 表数据一致性
- [ ] 验证封面文件存在性
- [ ] 验证 `cover_image_url` 字段格式
- [ ] 验证繁简转换完整性

---

## 📊 数据库架构

### albums 表（总表）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| album_id | INTEGER | 主键 |
| album_name | TEXT | 专辑名（简体） |
| artist | TEXT | 艺术家（简体） |
| release_year | TEXT | 发行年份 |
| total_listen_count | INTEGER | 总收听次数 |
| rating | REAL | 评分（1-5） |
| cover_image_url | TEXT | 封面 URL（`/covers/xxx.jpg`） |
| ... | ... | 其他字段 |

### albums_YYYY 表（年份表）

| 字段名 | 类型 | 说明 |
|--------|------|------|
| album_id | INTEGER | 主键 |
| album_name | TEXT | 专辑名（简体） |
| artist | TEXT | 艺术家（简体） |
| release_year | TEXT | 发行年份 |
| total_listen_count | INTEGER | 总收听次数 |
| rating | REAL | 评分（1-5） |
| cover_image_url | TEXT | 封面 URL（`/covers/xxx.jpg`） |
| ... | ... | 其他字段 |

**注意**：
- 两张表结构相同
- 判重依据：`album_name + artist`（非 `album_id`）
- 双表同步：写入年份表 + 总表

---

## 🎯 性能优化经验

### 1. 封面下载优化

**问题**：手动下载封面耗时

**解决方案**：
- 优先级：iTunes API > Deezer API > 网易云 API
- iTunes API 最稳定，封面质量高
- Deezer API 备选，封面质量中等
- 网易云 API 最后备选，封面质量低

**脚本化**：
- 实现 `_download_cover.py` 自动下载
- 批量下载未匹配封面的专辑

---

### 2. 数据库操作优化

**问题**：直接操作数据库可能锁死

**解决方案**：
- 操作前停止 Web 服务
- 操作后立即重启 Web 服务
- 使用事务（BEGIN/COMMIT）保证数据一致性

**脚本化**：
- 实现 `_add_album.py` 自动停止/重启服务
- 使用 Python `sqlite3` 模块操作数据库

---

### 3. Git 提交优化

**问题**：每次手动 Git 提交耗时

**解决方案**：
- 使用 Git Bash（有 credential helper）
- 编写 `git_add_commit_push.sh` 脚本
- 设置 Git 超时时间（`http.postBuffer`）

**脚本化**：
- 实现 `_add_album.py` 自动 Git 提交推送
- 捕获 Git 推送失败，稍后手动推送

---

## 📝 经验总结（每次操作后更新）

### 2026-05-27 操作经验

1. **封面文件路径规则**：
   - 封面必须放在 `album-tracker/public/covers/` 才能被 Web 访问
   - `\\10.0.2.4\qemu\原创计划\covers\` 是备份位置

2. **繁简转换规则**：
   - 繁体入库必须先转简体
   - `著` 字符有歧义，需人工核对

3. **PowerShell 禁用**：
   - 用户明确要求"杜绝使用powershell"
   - 所有命令改用 Python 或 CMD

4. **命令执行优先级**：
   - Python > CMD > Git Bash > PowerShell（禁用）

5. **Git 操作必须用 Git Bash**：
   - 原因：有 credential helper，能访问 Windows 凭据管理器

---

### 下次改进（2026-05-28 及以后）

- [ ] 完善 `_add_album.py`，实现全自动流程
- [ ] 实现 `_download_cover.py`，自动下载封面
- [ ] 实现 `_verify_album.py`，验证数据完整性
- [ ] 建立 album-tracker 操作日志（每次操作后记录）
- [ ] 定期回顾操作日志，提炼最佳实践

---

**最后更新**：2026-05-27
**维护者**：小飞 (XiaoFei)
**目标**：一次比一次准，一次比一次快，一次比一次少犯错
