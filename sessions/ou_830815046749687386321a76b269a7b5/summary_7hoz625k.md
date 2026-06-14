## 任务背景
用户想新建一个 album-site 项目，记录多个音乐数据网站的基本信息，为后续抓取和开发做准备。

## 执行过程
1. 用户发来 The Needle Drop 等四个网站
2. 用户要求建项目目录并记录信息
3. 用户要求为每个站点建独立目录（数据/脚本分离）
4. 用户陆续添加 Best Ever Albums、Acclaimed Music、Stereogum 三个新站点

## 关键结果
- 创建 `tasks/album-site/` 项目目录，含 7 个站点子目录（theneedledrop/allmusic/nme/chartmasters/besteveralbums/acclaimedmusic/stereogum），每个目录下 scripts/ 和 data/ 分离
- README.md 记录了每个站点的 URL、评分体系、反爬状况、页面结构和核心价值
- 期间多次 memory flush

## 结论建议
项目基础结构已建好，等待用户选择具体方向开始抓取或开发。