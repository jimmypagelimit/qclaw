# 专辑入库 - Panopticon - Det hjemsøkte hjertet

## 目标
入库专辑：Panopticon - Det hjemsøkte hjertet (2026)，听2次，RYM评分3.84

## 执行过程

### 1. 检查数据库状态
- 服务已在运行：http://localhost:3456
- 查询确认专辑不存在

### 2. 获取封面
- Deezer: 无结果
- iTunes: 找到封面 `https://is1-ssl.mzstatic.com/image/thumb/Music211/v4/0e/9c/01/0e9c0127-6ac2-c487-ea61-351f05a53e3e/7350142984199.png/600x600bb.jpg`

### 3. 数据库操作
- 停止Web服务（端口3456）
- 插入albums表：album_id=535, album_name='Det hjemsøkte hjertet', artist='Panopticon', release_year='2026', genre='Atmospheric Black Metal / Post-Metal', rating=3.84, total_listen_count=2, country='Norway'
- 插入albums_2026表：album_id=192
- 封面保存：`\\10.0.2.4\qemu\原创计划\covers\535-Panopticon-Det_hjemsokte_hjertet.jpg` (146KB)
- 导出database.sql

### 4. Git提交
- commit: `3a691a8` - "Add Panopticon - Det hjemsøkte hjertet (album_id=535, tc=2)"
- push: 成功

### 5. 重启服务验证
- albums count: 504 → 505 ✅
- totalListens: 1008 → 1010 ✅

## 结果
- **albums表**: 505条记录
- **albums_2026表**: 137条记录（新增一条）
- **封面**: 已下载保存
- **Git**: 已提交推送

## 技术发现
1. 数据库文件实际位置：`\\10.0.2.4\qemu\原创计划\music`（文件，非目录）
2. 表结构：
   - 评分字段名：`rating`（非`rym_rating`）
   - 主键：albums表用`album_id`，albums_2026表用`album_id`（非`id`）
3. cover目录：`\\10.0.2.4\qemu\原创计划\covers\`

## 文件
- 入库脚本：`C:\Users\qujt\.qclaw\workspace\_add_album.py`
- Git脚本：`C:\Users\qujt\.qclaw\workspace\_git_push.sh`

---
*完成时间：2026-05-27 12:27*