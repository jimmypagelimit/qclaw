# 歌词功能修复报告 — 2026-06-19

## 核心突破：opencli 已登录态抓取网易云歌词

**问题**：部分专辑（嘎调、东京酒吐座、施鑫文月、葬尸湖）在网易云需要登录才能获取歌词，API 返回 `code=-462`（需绑定手机）。

**解决方案**：`opencli browser work eval` + `credentials:'include'`
```python
# 通过已登录浏览器 session 调用网易云 API
js = "fetch('/api/album/{id}',{credentials:'include'}).then(r=>r.json())..."
subprocess.run('opencli browser work eval ' + json.dumps(js))
# 再 eval "window.__wy" 读取 JSON 结果
```
两步法绕过登录限制：Step1 触发 fetch 存入 `window.__wy`，Step2 读取结果。

## 修复成果

| 专辑 | DB ID | 结果 |
|------|-------|------|
| 嘎调 - 嘎调 | 444 | 12/12 曲目 → DB路径已写入（2首器乐无歌词文件） |
| 施鑫文月 - 灰太阳 | 425 | 8/8 曲目 → 文件存在+路径已修复 |
| 东京酒吐座 - Remains | 515 | 8首（1首 Wisteria 有歌词，其他英文靠 LRCLIB） |
| 葬尸湖 - 冬霾 | 291 | 2首器乐，网易云确实无歌词 |

## 关键技术细节

1. **GBK控制台处理**：Windows 控制台 GBK 编码，用 `python.exe -X utf8` 或 `sys.stdout.reconfigure(encoding='utf-8')` 绕过
2. **路径处理**：DB 存 UTF-8 路径，`os.path.exists()` 在 Python 内正常，用 `os.listdir()` + `sys.stdout.reconfigure` 扫描中文目录
3. **文件匹配**：按 `track_no` 匹配比按 track_name 更可靠（中文名 vs 英文名不匹配时）
4. **subprocess 引号**：用 `json.dumps(js_code)` 生成带引号的 shell 参数，避免 PowerShell 转义问题

## 当前歌词覆盖率

- **曲目**：2595/4958（52%）
- **专辑**：343/462（74%）

## 剩余问题

- 葬尸湖《奕秋》《孤雁》等：网易云无收录，需其他来源
- 英文专辑歌词：主要靠 LRCLIB，命中率较高
- DB track_name 字段部分中文为 GBK 残留显示（实际值正确）
