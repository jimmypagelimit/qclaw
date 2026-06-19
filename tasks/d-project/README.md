# D项目 — 豆瓣音乐数据管道

> 2026-06-19 立项

## 定位

从豆瓣音乐系统化获取中文专辑元数据，作为N项目(匿名旅行者)和W项目(网易云音乐)的补充。

## 核心价值

### 豆瓣评分（最独特的价值）
- 十分制评分，中文独立音乐社区最活跃
- 覆盖比匿名旅行者更广，冷门中文专辑也有评分
- 评分分布：7.0-7.9一般，8.0-8.5优秀，8.6-9.2经典
- 评分人数：冷门专辑50-200人，热门500-2000人，经典2000+

### 豆瓣标签
- 用户自定义标签体系（后摇/独立/民谣等）
- 比网易云更细的风格分类
- 高频标签可转化为标准风格

### 豆瓣评论
- 热门短评：2-5条精华用户短评
- 长评系统：有价值的深度乐评
- 条目介绍页：专辑描述（网易云常有而豆瓣无的互补）

### 曲目数据
- 标准曲目列表（含时长）
- 推荐歌曲标记（豆瓣用户投票推荐）
- 多个版本区分

### 外部ID桥接
- 豆瓣ID ↔ 网易云ID ↔ MBID 的跨源映射
- 匿名旅行者的 `links` 字段已有豆瓣ID → 可作为搜索入口

## 已知限制与反爬

- **公开页面**: `https://music.douban.com/subject/{id}/` 可公开访问
- **反爬措施**: 高频请求会触发验证码或封IP
- **建议频率**: 每请求间隔1-2秒
- **API限制**: `api.douban.com` V2需OAuth认证（不推荐用）
- **页面结构**: HTML渲染，非SPA，适合静态解析

## 与其他项目的关系

| 项目 | 互补点 |
|------|--------|
| N项目(匿名旅行者) | 两者都有豆瓣ID，可双向打通。匿名旅行者有郭佳评论，豆瓣有社区评分 |
| W项目(网易云音乐) | 网易云有曲目时长+封面，豆瓣有评分+标签 |
| L项目(歌词) | 豆瓣不提供歌词，不相关 |

### 数据优先级
1. **豆瓣评分** → 写入 `external_ratings` 表（source='douban', score_scale='10'）
2. **豆瓣标签** → 映射为标准风格后写入 `album_styles`
3. **豆瓣短评** → 筛选高赞2-5条，补充到专辑描述
4. **曲目** → W项目优先，豆瓣作为备选

## Python调用示例

```python
import urllib.request
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"
}

# 专辑页
url = f"https://music.douban.com/subject/{douban_id}/"
req = urllib.request.Request(url, headers=headers)
resp = urllib.request.urlopen(req)
soup = BeautifulSoup(resp.read(), "html.parser")

# 评分
rating = soup.select_one(".rating_num")
score = float(rating.text.strip()) if rating else None

# 评分人数
rating_people = soup.select_one(".rating_people span")
votes = int(rating_people.text.strip()) if rating_people else 0

# 曲目列表
tracklist = soup.select(".track-list .track-item")
# ... 需要具体解析
```

## 数据库待补清单

### 可尝试通过豆瓣补的专辑
从匿名旅行者搜不到的6张中，可尝试用豆瓣ID直查：
- 超载《超载》(ID 33) — 豆瓣大概率有
- 子曰《第一册》(ID 99) — 豆瓣大概率有
- 深山《雪山白凤凰》(ID 106) — 有
- 缺省《共同的土地》(ID 448) — 较新，可能有

### 已知豆瓣ID（来自匿名旅行者）
| album_id | 专辑 | 豆瓣ID |
|----------|------|--------|
| 51 | 谁都看见了希望 | - |
| 96 | 近人可读 | 35101591 |
| 440 | 没有鸟鸣，关上窗吧 | 33446085 |
| 445 | 城市天气的航行 | 3118264 |
