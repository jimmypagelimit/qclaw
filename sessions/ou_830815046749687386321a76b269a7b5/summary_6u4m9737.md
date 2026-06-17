## 任务背景
用户在A项目（album-tracker）的专辑详情页，需要展示曲目列表(tracks)和外部评分(RYM/Pitchfork)等卫星表信息。

## 执行过程
1. 改造server.ts：详情API新增tracks、external_ratings、review_url查询
2. 改造前端UI：app.js新增tracks/ratings渲染函数，style.css新增对应样式
3. 修复多个bug：处理total_listen_count废弃字段、external_reviews表不存在问题
4. TypeScript编译、重启服务、API验证、git push

## 关键结果
- 后端API：专辑详情接口返回tracks(曲名/曲序/时长)、external_ratings(RYM蓝色+Pitchfork橙色badge)、review_url、实时listen_count
- 前端UI：曲目列表+外部评分卡片已集成
- 服务运行中：http://localhost:3456
- Commit: `82be746`，已push

## 结论建议
功能已完成并部署。已知限制：tracks数据仅覆盖3.4%、外部评分仅24.8%，建议后续批量补充。