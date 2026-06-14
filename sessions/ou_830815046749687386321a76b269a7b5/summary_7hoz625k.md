## 任务背景
用户测试 RateYourMusic 爬虫，遇到 Cloudflare Turnstile 验证拦截；后讨论 MusicBrainz API 集成到专辑项目。

## 执行过程
1. RYM CloakBrowser 测试：Turnstile 验证码卡住
2. 升级 cloakbrowser 至 v0.3.31（已最新）仍失败
3. 用户决定明天再试，记录暂停至 artifact
4. 讨论 MusicBrainz API 使用情况
5. 实测各接口：搜索 API 通，但 release-group 和 Cover Art SSL 失败
6. 更新 PLAN-TRI-MERGE.md 集成 MusicBrainz

## 关键结果
- RYM 爬虫暂停，Cloudflare 升级拦截
- MusicBrainz 搜索 API 可用，但 genre/cover 因 Python SSL 问题不可用
- 更新 `tasks/album-site/PLAN-TRI-MERGE.md` 第九节

## 结论建议
明天 heartbeat 自动重试 RYM；MusicBrainz 搜索 API 可先用（查 MBID/年份），Cover Art 需另寻源。