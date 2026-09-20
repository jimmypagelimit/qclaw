# L项目进展：2026-09-20 路径修复 + 批量补齐（Linux环境迁移后）

## 背景
L项目此前运行在 Windows 环境（`C:\Users\qujt\...`），歌词目录与数据库已迁移到 Linux（`/root/qclaw/tasks/lyrics-expert/lyrics` + `album-tracker/music`）。

## 本次成果

### 1. 歌词路径全面修复
- **发现**：`src/server.ts` 歌词 API 是旧版（直接用相对路径读文件，全部 miss）；实际运行的是 `dist/server.js`（7-30编译，`join(lyricsRoot, path)` 正确）。**src 未同步**，重编译会丢修复
- **修复**：`src/server.ts` 同步为 dist 相同逻辑（`path.join(lyricsRoot, '..','..','..','lyrics-expert','lyrics')` 拼接）
- **坏路径清零**：数据库里约 80 条歌词路径损坏（Windows绝对路径 `C:\...`、`lyrics/`前缀、目录尾点 `U.F.O.F.`vs`U.F.O.F`、简繁目录名差异），已全部修到磁盘精确可读
- **验证**：`/api/albums/:id/lyrics` 全量无缺失文件

### 2. 批量补齐歌词（fill_missing_lyrics.py）
新管道：英文→LRCLIB、中文→网易云，写完自动更新数据库相对路径

| 专辑 | 结果 |
|------|------|
| Carly Rae Jepsen - Day and Night | 23/25 |
| 高枫 - 美丽新世界 | 20/21 |
| 陈绮贞 - 花的姿态演唱会经典实录 | 18/18 |
| The Microphones - The Glow, Pt. 2 | 16/20 |
| 罗大佑 - 春龙交响夜2024 | 16/19 |
| The Clash - London Calling | 25/40 |
| Funeral Mist / War Child / John Lennon | 低（器乐/demo 客观无词） |

### 3. 覆盖率变化（三轮批量 + 手工补专辑后）
| 指标 | 之前 | 现在 |
|------|------|------|
| 总曲目 | 6722 | 6722 |
| LRC | 3913 (58.2%) | **4523 (67.0%)** |
| TXT | 4506 | **5097 (75.8%)** |
| 磁盘缺失文件 | 多处 | **0** |

### 4. 三轮批量命中明细
**批1（--top 8）**：Carly Rae Jepsen 23/25、高枫 20/21、陈绮贞花的姿态 18/18、The Microphones 16/20、罗大佑春龙 16/19
**批2（--top 12）**：魏如萱大事发声 18/18、夏之禹 17/17、罗大佑美丽岛 16/16、Phoebe Bridgers 16/17、Lady Gaga MAYHEM 15/15、Doolittle 15/15、Californication 15/15、张雨生卡拉OK台北我 13/13
**批3（--top 15）**：Loathe 14/14、Blur 13/14、熊天平 13/13、王齐铭生活麻辣烫 13/13、苏紫旭泪水与共 12/13、AKRIILA 10/14
**批4（手工精选）**：The Stone Roses 12/12、Madonna Confessions II 12/12、Big Thief U.F.O.F. 12/12、张悬亲爱的我还不知道 11/11、陈绮贞华丽的冒险 11/11、反光镜 12/12、郑源 12/12、Wednesday 12/12、宝岛咸酸甜 12/12、刺猬乌鸦谷 12/12、Natalia 12/12、王菲唱游 12/12、罗大佑首都11/13、吴青峰马拉美9/12

### 5. 客观难啃（预期内，不冒险补）
- **Funeral Mist - Salvation (26)**：器乐黑金属，全 miss
- **War Child Help(2) (21)**：杂锦合辑首发英语援助，LRCLIB 无
- **John Lennon - Plastic Ono Band (18)**：Lennon 精选封面 Take，LRCLIB 只中 1
- **Car Seat Headrest demo (17)、The Clash London Calling demo (15)**：bootleg/demo 录音
- **Maria BC Marathon (12)、Mägo de Oz (6/12)**：冷门/改编曲，LRCLIB 部分缺失

## 剩余工作
- 剩余缺口以客观限制为主：器乐/黑金/demo/冷门
- 后续可做：LRC 时间轴校对、双语翻译补全，或对新入库专辑增量跑本管道

## 脚本位置
- `tasks/lyrics-expert/fill_missing_lyrics.py`（--album ID / --top N）

---
*时间：2026-09-20*