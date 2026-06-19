# W项目 — 网易云音乐数据管道

> 2026-06-19 立项

## 定位

通过网易云音乐API系统化获取专辑元数据（曲目、封面、描述、评论），作为中文专辑数据的主力补充源。

## 已知能力

### API端点
- **搜索**: `GET /api/search/get?s={keyword}&type=10&offset=0&limit=30`
- **专辑详情**: `GET /api/album?id={album_id}`
- **艺人专辑**: `GET /api/artist/albums/{artist_id}?limit=50&offset=0`
- **歌词**: `GET /api/song/lyric?id={song_id}&lv=1`

### 请求要求
- **Referer头**: 必须设置 `Referer: https://music.163.com`
- **User-Agent**: 需设置浏览器UA
- **反爬限制**: 频繁请求会触发-462错误（需手机绑定），建议间隔500ms+
- **地域限制**: 部分海外专辑返回错误

### 已验证数据
- 专辑名、艺人名、发行日期、曲目列表（含时长）
- 封面图URL（高质量，800px+）
- 专辑描述（中文，约30-50字）
- 网易云专辑ID（在匿名旅行者的online_links中有对应）

### 已知问题
- **-462错误**: 部分专辑需手机绑定网易云账号才能获取
- **封面质量**: 部分返回低质量或错误封面
- **描述偏短**: 网易云描述通常30-50字，信息量有限
- **冷门缺失**: 极冷门独立专辑可能不在网易云库中

## 数据库写入规则

1. 描述字段：来源标记 `[网易云]`
2. 曲目：从tracklist提取，含时长（秒），source='netease'
3. 封面：优先级最高（网易云API > iTunes > RYM），下载至 `album-tracker/public/covers/`
4. 网易云专辑ID：存入 `external_ratings` 表（source='netease'）或专辑links字段

## 数据库待补全清单

### 缺描述的专辑（25张→21张，4张已由匿名旅行者补全）
优先用网易云补描述（比匿名旅行者覆盖更广）

### 缺曲目的专辑（56张→53张）
网易云有完整曲目+时长数据，是补曲目首选源

### 缺封面的专辑（~14张）
网易云封面质量高，优先下载

## 与其他项目的关系

| 项目 | 关系 |
|------|------|
| N项目(匿名旅行者) | 互补：匿名旅行者有郭佳短评+评分，网易云有曲目时长+封面 |
| L项目(歌词) | W项目提供网易云歌词作为中文歌词源 |
| 专辑追踪器主库 | W项目是中文专辑数据的主补全源 |

## Python调用示例

```python
import urllib.request, json

headers = {
    "Referer": "https://music.163.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0"
}

# 搜索专辑
url = f"https://music.163.com/api/search/get?s={urllib.parse.quote(query)}&type=10&offset=0&limit=10"
req = urllib.request.Request(url, headers=headers)
data = json.loads(urllib.request.urlopen(req).read())

# 获取专辑详情
url = f"https://music.163.com/api/album?id={album_id}"
req = urllib.request.Request(url, headers=headers)
data = json.loads(urllib.request.urlopen(req).read())
```

## 下一步
1. 批量搜索缺描述+缺曲目的专辑，匹配网易云ID
2. 补全曲目（含时长，比匿名旅行者更完整）
3. 补全封面（下载高质量图）
4. 补全描述（中文专辑主力源）
