# ALBUM_TRACKER_RULES.md - album-tracker 操作手册

> **核心目标**：每次操作都更准、更快、更少犯错
> **使用方法**：每次操作 album-tracker 前，先读 MEMORY.md 概览，再读本手册获取操作细节

---

## 📋 标准操作流程（SOP）

### 新增专辑完整流程（2026-06-08 重构）

**每次用户说"听了一张专辑"或"新增专辑"时，必须执行完整流程：**

1. ✅ **停止 Web 服务**（避免 sqlite3 锁冲突）
   ```bash
   tasklist | findstr node
   taskkill /PID <pid> /F
   ```

2. ✅ **写入数据库**（单表模式）
   - 判重：`SELECT album_id FROM albums WHERE album_name=? AND artist=?`
   - 不存在 → 插入 `albums` 表，写入 `listen_history` 表
   - 已存在 → 只增加 `total_listen_count`，新增 `listen_history` 记录

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
   ```

7. ✅ **导出 `database.sql`**
   ```python
   import sqlite3
   conn = sqlite3.connect(r'\\10.0.2.4\qemu\原创计划\music\music')
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

### 错误6：listen_history album_id 映射错误（2026-06-08 修复）

**症状**：
- 年度排行显示的专辑名与用户实际听的不符
- 例如：用户 2026 年听了海朋森-沙之小説，但系统显示朴树-露露电影院

**根因**：
- `listen_history` 表中的 `album_id` 引用错误
- 原因：旧版迁移时，直接从年度表（`albums_2024/2025/2026`）拷贝 ID，但年度表的自增 ID 与 `albums` 总表的 ID 不对应

**解决**（已执行）：
1. 备份 `_music_latest.db`（备份文件 `_music_latest.db.bak.before_rebuild`）
2. 从年度表重新映射 `(album_name, artist)` → `albums` 表的正确 `album_id`
3. 重建 `listen_history` 表（清空后重新插入）
4. 对于年度表中不存在于 `albums` 表的专辑，先插入 `albums` 表再建立映射
5. 导出 `database.sql`，Git 提交推送

**预防**：
- 严禁直接使用年度表的 ID 作为 `album_id` 写入 `listen_history`
- 所有 `album_id` 引用必须通过 `(album_name, artist)` 映射获取
- 定期运行 `_audit_mapping.py` 检查数据一致性

---

## 🔧 工具脚本清单

### 1. `_add_album.py` - 新增专辑（待完善）

**功能**：
- 自动执行标准操作流程（10步）
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
- 批量转换 albums 表中的繁体中文为简体
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
- [ ] 自动复制到 Web 路径

---

### 4. `_verify_album.py` - 验证专辑数据（待完善）

**功能**：
- 验证专辑数据完整性
- 检查封面文件是否存在
- 检查 `cover_image_url` 字段是否正确
- 检查繁简转换是否完整
- 检查 `listen_history` 映射是否正确

**当前状态**：❌ 未实现

**待实现**：
- [ ] 验证 albums 表数据完整性
- [ ] 验证封面文件存在性
- [ ] 验证 `cover_image_url` 字段格式
- [ ] 验证繁简转换完整性
- [ ] 验证 `listen_history` 映射正确性（运行 `_audit_mapping.py`）

---

### 5. `_audit_mapping.py` - 审计 album_id 映射 ✅

**功能**：
- 检查 `listen_history` 表中的 `album_id` 是否引用正确
- 对比年度表（`albums_2024/2025/2026`）的 `(album_name, artist)` 与 `albums` 表的映射
- 输出不匹配的记录

**使用方法**：
```bash
cmd /c "C:\Python311\python.exe _audit_mapping.py"
```

**当前状态**：✅ 已实现（2026-06-08）

---

### 6. `_rebuild_listen_history.py` - 重建 listen_history 表 ✅

**功能**：
- 从年度表重新映射 `(album_name, artist)` → `albums` 表的正确 `album_id`
- 重建 `listen_history` 表（清空后重新插入）
- 处理缺失专辑（插入 `albums` 表）

**使用方法**：
```bash
cmd /c "C:\Python311\python.exe _rebuild_listen_history.py"
```

**注意**：运行前会自动备份 `_music_latest.db`

**当前状态**：✅ 已实现（2026-06-08）

---

## 📊 数据库架构（2026-06-08 重构后）

### albums 表（总表）✅

| 字段名 | 类型 | 说明 |
|--------|------|------|
| album_id | INTEGER | 主键（自增） |
| album_name | TEXT | 专辑名（简体） |
| artist | TEXT | 艺术家（简体） |
| release_year | TEXT | 发行年份 |
| total_listen_count | INTEGER | 总收听次数 |
| rating | REAL | 评分（1-5） |
| cover_image_url | TEXT | 封面 URL（`/covers/xxx.jpg`） |
| country | TEXT | 国家 |
| region | TEXT | 地区（从 country 推导） |
| genre | TEXT | 流派（文本，冗余字段） |
| style | TEXT | 风格（文本，冗余字段） |
| duration | TEXT | 时长（MM:SS 格式） |
| release_company | TEXT | 发行公司 |
| producer | TEXT | 制作人 |
| description | TEXT | 描述 |
| is_compilation | INTEGER | 是否合辑（0/1） |
| first_listen_date | TEXT | 首次收听日期 |
| rym_rating | REAL | RYM 评分（/5） |
| rym_ratings_count | INTEGER | RYM 评价数 |
| rym_url | TEXT | RYM 专辑 URL |

**注意**：
- `genre` 和 `style` 是文本字段（冗余），同时也有中间表 `album_genres` 和 `album_styles`
- 判重依据：`album_name + artist`（非 `album_id`）

---

### listen_history 表 ✅

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | INTEGER | 主键（自增） |
| album_id | INTEGER | 外键 → albums.album_id |
| listen_date | TEXT | 收听日期（YYYY-MM-DD） |
| listen_year | INTEGER | 收听年份（用于年度统计） |
| notes | TEXT | 备注 |
| source | TEXT | 来源（如"用户口述"、"Web界面"） |

**注意**：
- 每条记录代表一次收听
- 年度统计通过 `SELECT COUNT(*) FROM listen_history WHERE listen_year=2026 AND album_id=?` 获取
- **严禁**直接使用年度表的 ID 作为 `album_id`

---

### album_genres 表（中间表）✅

| 字段名 | 类型 | 说明 |
|--------|------|------|
| album_id | INTEGER | 外键 → albums.album_id |
| genre_id | INTEGER | 外键 → genres.genre_id |
| genre_order | INTEGER | 排序（从 0 开始） |

---

### album_styles 表（中间表）✅

| 字段名 | 类型 | 说明 |
|--------|------|------|
| album_id | INTEGER | 外键 → albums.album_id |
| style_id | INTEGER | 外键 → styles.style_id |
| style_order | INTEGER | 排序（从 0 开始） |

---

### artists 表 ✅

| 字段名 | 类型 | 说明 |
|--------|------|------|
| artist_id | INTEGER | 主键（自增） |
| artist_name | TEXT | 艺术家名（简体） |
| country | TEXT | 国家 |
| region | TEXT | 地区 |
| description | TEXT | 描述 |

---

### genres 表 ✅

| 字段名 | 类型 | 说明 |
|--------|------|------|
| genre_id | INTEGER | 主键（自增） |
| name | TEXT | 流派名 |

---

### styles 表 ✅

| 字段名 | 类型 | 说明 |
|--------|------|------|
| style_id | INTEGER | 主键（自增） |
| name | TEXT | 风格名 |

---

### 已废弃的年度表 ❌

以下表已废弃（2026-06-08），不再使用：
- `albums_2024`
- `albums_2025`
- `albums_2026`

**原因**：
- 年度表的自增 ID 与 `albums` 总表不对应，导致 `listen_history` 映射错误
- 维护成本高（每次新增专辑需写入两张表）
- 统计逻辑复杂（需要 UNION 多张表）

**替代方案**：
- 使用 `listen_history` 表 + `albums` 表 JOIN 实现年度统计
- 示例：`SELECT a.album_name, a.artist, COUNT(lh.id) as cnt FROM listen_history lh JOIN albums a ON lh.album_id = a.album_id WHERE lh.listen_year = 2026 GROUP BY lh.album_id ORDER BY cnt DESC`

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

### 2026-06-08 重构经验

1. **数据库架构重构**：
   - 废除年度表（`albums_2024/2025/2026`）
   - 使用单表 `albums` + `listen_history`
   - 年度统计通过 `listen_history` + `albums` JOIN 实现

2. **listen_history 映射错误修复**：
   - 根因：年度表 ID 与总表 ID 不对应
   - 解决：重建 `listen_history`，按 `(album_name, artist)` 映射
   - 预防：严禁直接使用年度表 ID

3. **Web 查询逻辑更新**：
   - 修改 `server.ts` 4个API端点（`/api/stats`、`/api/albums`、`/api/genres`、新增`/api/styles`）
   - 使用 JOIN 查询替代合并文本
   - 前端 `index.html` 和 `app.js` 同步更新（废弃年度表引用）

4. **数据备份**：
   - 重建前自动备份 `_music_latest.db`
   - 备份文件命名：`_music_latest.db.bak.YYYYMMDD`

---

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

### 下次改进（2026-06-09 及以后）

- [ ] 完善 `_add_album.py`，实现全自动流程
- [ ] 实现 `_download_cover.py`，自动下载封面
- [ ] 实现 `_verify_album.py`，验证数据完整性
- [ ] 建立 album-tracker 操作日志（每次操作后记录）
- [ ] 定期回顾操作日志，提炼最佳实践
- [ ] 定期运行 `_audit_mapping.py` 检查数据一致性

---

**最后更新**：2026-06-08
**维护者**：小飞 (XiaoFei)
**目标**：一次比一次准，一次比一次快，一次比一次少犯错
