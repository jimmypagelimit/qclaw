# L项目管道跑通 + Gemini音乐数据库报告学习

## 时间
2026-06-15 07:22

## L项目（Lyrics Expert）管道完成
- **方案**: Playwright(MusicBrainz曲目表) → LRCLIB(歌词) → 本地保存
- **验证**: Car Seat Headrest - Twin Fantasy, 10/10首全部成功
- **输出**: 18个文件（8首.lrc+.txt, 2首仅.txt）, 路径: tasks/lyrics-expert/lyrics/
- **关键修复**: MB release-group页面链接是 /release/xxx/cover-art 格式，需去掉/cover-art后缀
- **限制**: LRCLIB无中文歌词；MB频繁请求会被限流(ERR_CONNECTION_CLOSED)
- Git commit: 0325b7e

## Gemini Deep Research 报告学习
- 来源: https://g.co/gemini/share/0f41579a124b
- 标题: 《全球独立与极端音乐学术文献及数字产品数据架构评估报告》
- 内容: 47个全球核心音乐数据库全景盘点 + 元数据生态传导机制分析
- 核心架构原则: ①核心标识符解耦(MBID三层:Release Group/Release/Recording) ②算法+人类标签共生 ③录音学分源头采集(DDEX RIN)
- 对A项目影响: 应加release_mbid字段，接入MusicBrainz全局标识符
- 对R项目影响: RYM流派树和加权评分的学术价值再次确认
- 对L项目影响: 可扩展LyricsTranslate(多语种翻译)和Musixmatch(时间戳对齐)
- 新发现: WhoSampled(采样链)、Every Noise at Once(6000+微型流派)、SecondHandSongs(翻唱追溯)
