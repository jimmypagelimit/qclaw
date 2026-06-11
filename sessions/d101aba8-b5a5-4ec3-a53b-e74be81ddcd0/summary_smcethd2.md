## 任务背景
用户要求按周四例行检查Metal/Hardcore RSS源，汇总6月10-11日的重要动态并发送到飞书群。

## 执行过程
1. 读取RSS源清单（9个Metal/Hardcore源）
2. 并行抓取所有RSS feed
3. 筛选6月10-11日条目
4. 按"新专辑/巡演/地下发现/硬核动态"分类整理
5. 尝试发送飞书但跨上下文被拒

## 关键结果
- **Khemmis同名第五张专辑** 获NCS+AMG双覆盖（AMG 3.5/5）
- **Left To Die（ex-Death成员）** 处女专辑7月17日发，第二首单曲已出
- **Acid Bath & Ministry** Red Rocks+芝加哥演出官宣
- Lambgoat最活跃（2天15+条），No Echo无近期更新
- 荒岛唱片收藏艺术家（Sonic Youth/U2等）本周无新闻
- 摘要已保存至 `metal_hardcore_digest_20260611.md`
- ❌ 飞书发送失败：webchat会话无法跨provider发送

## 结论建议
摘要文件已就绪，需要主Agent在飞书绑定的会话中重发。建议下周四提前确保主会话有飞书通道权限。