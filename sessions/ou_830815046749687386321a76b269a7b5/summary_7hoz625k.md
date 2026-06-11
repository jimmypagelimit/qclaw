## 任务背景
用户需要将 Porcelain Stars 的专辑 Rosemary 信息入库到音乐数据库。
## 执行过程
1. 定位专辑信息（Apple Music/Spotify/Reddit 等来源）
2. 排查 SQLite 数据库路径（NAS 不通，本地多次尝试后找到 _music_latest.db）
3. 从 iTunes 获取封面和曲目
4. 执行入库（首次因封面 404 回滚，重试成功）
5. 清理临时脚本，写入每日记忆文件
## 关键结果
- Porcelain Stars - Rosemary 成功入库（album_id: 551）
- 风格: Alternative，9首/26min，封面已下载
- 临时生成脚本已全部清理
- 记忆已写入 memory/2026-06-11.md
## 结论建议
数据库已恢复正常可用，后续可继续抓取 RYM 评分或入库更多专辑。