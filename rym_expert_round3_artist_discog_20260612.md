# RYM Expert Round 3: 艺人页数据提取

**时间**: 2026-06-12 09:42 (cron)
**任务**: 提取艺人页完整数据（碟库+相关艺人+流派+简介）

## 结果

3/3 艺人全部成功提取:

| 艺人 | 碟库数 | 流派 | 相关艺人 | 简介 |
|------|--------|------|----------|------|
| Car Seat Headrest | 46 | Slacker Rock, Indie Rock, Singer-Songwriter | 1 | 无 |
| Sonic Youth | 41 | Noise Rock, Alternative Rock, Experimental Rock | 16 | 有 |
| The Cure | 60 | Post-Punk, Alternative Rock, Gothic Rock | 6 | 有 |

## 数据文件

- `tasks/rym-expert/data/artists/{slug}_discog.json` — 结构化数据
- `tasks/rym-expert/data/artists/{slug}_full.html` — 原始HTML
- `tasks/rym-expert/data/artists/{slug}_full.png` — 截图

## 关键技术发现

1. RYM 艺人页 Genre 在 `<meta name="description">` 中，不在链接中
2. Descriptives（用户标签）仅专辑页有，艺人页没有
3. Related Artists 在 "Related" section 中
4. Discography 正则: `disco_release` div → `disco_avg_rating` + `disco_ratings` + `disco_reviews` + `<a class="album">` + `disco_year_ymd`
5. 脚本: `tasks/rym-expert/scripts/rym_artist_v2.py` v3

## CSH Top 5 评分

1. Sunburned Shirts 4.50 (2 ratings)
2. Beach Life-in-Death 4.27 (2106)
3. Little Pieces of Paper 4.22 (57)
4. Bodys 4.20 (1339)
5. Drunk Drivers/Killer Whales 4.11 (1336)

## 下一步

- Round 4: 更多艺人 / 流派 Charts Top 50 / Pop/Metal 流派树
