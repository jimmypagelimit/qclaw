# RYM Expert 项目建立 - 任务记录
**时间**：2026-06-11 13:41
**目标**：将 RYM 探索从临时任务升级为系统化长期项目

---

## 项目结构

```
tasks/rym-expert/
├── README.md           # 项目总览+进度追踪
├── DATA-CATALOG.md     # 数据目录
├── scripts/
│   ├── explore_rym.py      # 综合探索脚本（heartbeat调用）
│   └── extract_charts.py   # Charts数据提取
├── data/
│   ├── charts/             # 排行榜数据
│   │   ├── chart_data.json     # 76张专辑原始数据
│   │   └── comparison.json     # 用户收藏对比结果
│   └── genres/             # 流派数据
│       └── rock-style-tree.json
├── docs/
│   └── EXPERT-GUIDE.md     # 专家能力图谱
└── explorations/           # 每次探索记录
```

## 首次 Charts 对比结果

- 用户收藏：516 张专辑
- All-Time Top 38：16/38 已拥有（42%）
- 2010s Top 38：4/38 已拥有（11%）

### Top 5 缺失高分专辑
1. Pink Floyd - Wish You Were Here (4.37/5)
2. King Crimson - In the Court of the Crimson King (4.33/5)
3. Madvillain - Madvillainy (4.33/5)
4. Stevie Wonder - Songs in the Key of Life (4.31/5)
5. John Coltrane - A Love Supreme (4.30/5)

## Heartbeat 执行策略

每次 heartbeat 调用 `scripts/explore_rym.py --task auto`：
1. Charts 对比（发现遗漏经典）
2. 流派深入（抓取子流派+Top专辑）
3. 新功能测试（艺人页/发片日历等）
4. 更新知识库

## Git
- rym-expert 项目独立仓库：commit 5487878
- workspace 主仓库：commit 8845b72
