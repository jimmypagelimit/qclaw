# N项目 — 匿名旅行者（AnonTraveler）数据管道

> 2026-06-19 立项

## 定位

从 anontraveler.com 系统化获取中文独立音乐专辑元数据，补充数据库中缺失的描述、曲目、评分、风格等信息。

## 已知能力

### API端点（需Playwright浏览器session）
- **搜索**: `GET /api/meta/quick_search/all?kw={keyword}`
- **专辑详情**: `GET /api/meta/album/{at_id}`
- **艺人详情**: `GET /api/meta/artist/{at_id}`
- **流派图书馆**: `GET /genre/` 页面

### 搜索规则
1. **必须通过Playwright浏览器上下文调API**（需先visit站点获取session/cookie，API直调返回空）
2. **短词（<4字）搜不到**，需用完整专辑名
3. **键盘输入+XHR拦截**是最可靠的搜索方式（`page.type(query, delay=150)` + 监听response）
4. **`page.evaluate(fetch)`** 在有session时可获取专辑详情API
5. 匿名旅行者使用Vue 3 SPA架构

### 数据结构（专辑详情）
```json
{
  "title": "专辑名",
  "main_artist": {"name": "艺人", "_id": "at_id"},
  "year": 1998,
  "tracklist": [{"title": "1.曲名", "position": 1}],
  "styles": [{"name": "风格", "name_orig": "Style"}],
  "relate_styles": [{"name": "关联风格"}],
  "rating_anon": 94,
  "rocknuts": [{"content": "评论", "score": 0, "rank_order": 1, "title": "榜单名"}],
  "online_links": {"netease": {"url": "网易云链接"}},
  "links": [{"site": "douban/musicbrain", "url": "..."}],
  "primary_img": "封面URL",
  "album_type": {"name": "录音室专辑"},
  "contribute_user": [{"name": "郭佳"}]
}
```

### 曲目格式注意
- 曲目标题格式为 `"1.曲名"`（数字前缀+点），需提取序号后的歌名
- 无时长数据（duration字段缺失）
- 部分专辑曲目为空（"未人工处理"状态）

## 郭佳短评

匿名旅行者核心贡献者，其"rocknuts"评论是高价值数据：
- 榜单系统：Version Album类型，含rank_order和score
- 内容：短评正文在content字段
- 已见榜单：最佳华语流行专辑90s/00s [2025重置版]、各年最爱华语专辑、荒岛余生、华语最佳500张发行等

## 数据库写入规则

1. 描述字段：风格 + 郭佳/用户短评 + 外部ID（豆瓣/网易云/MBID）
2. 曲目：从tracklist提取，去数字前缀，duration置NULL，source='anontraveler'
3. 评分：写入 external_ratings 表（source='anontraveler', score_scale='100'）
4. 风格：暂不入库（风格体系与RYM不同，需映射）

## 数据库待补全清单

### 高优先级（缺描述+缺曲目）
| album_id | 专辑 | 艺人 | 状态 |
|----------|------|------|------|
| 95 | 两伊战争 | 张雨生 | ❌匿名旅行者未处理 |
| 33 | 超载 | 超载 | ❌搜不到 |
| 106 | 雪山白凤凰 | 深山 | ❌搜不到 |
| 99 | 第一册 | 子曰 | ❌搜不到 |
| 448 | 共同的土地 | 缺省 | ❌搜不到 |
| 327 | 夜官巡场 | 装咖人 | ❌搜不到 |
| 443 | She Came Back From the Square | 海朋森 | ❌搜不到 |
| 22 | 同名专辑 | 王啸坤 | 待搜 |
| 25 | 红楼梦 | 陈力 | 待搜 |
| 68 | 王菲1997 | 王菲 | 待搜 |
| 43 | 望乡 | 陈升 | 待搜 |
| 80 | 寂寞星空见歌 | 李健 | 待搜 |
| 76 | 校园民谣 | 群星 | 待搜 |

### 已完成
| album_id | 专辑 | 艺人 | 补全内容 |
|----------|------|------|---------|
| 51 | 谁都看见了希望 | 李杰 | 描述+9曲目+评分94 |
| 96 | 近人可读 | 寸铁 | 描述+9曲目 |
| 440 | 没有鸟鸣，关上窗吧 | 声音碎片 | 描述+10曲目 |
| 445 | 城市天气的航行 | P.K.14 | 描述+18曲目 |
| 95 | 两伊战争 | 张雨生 | 仅描述（无曲目数据） |

## 下一步
1. 搜索剩余待补全专辑（用艺人名+专辑名组合）
2. 探索艺人页API（可能获取艺人全部专辑列表）
3. 提取郭佳评论/榜单数据（高价值文本）
