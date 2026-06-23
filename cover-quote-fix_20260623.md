# 封面文件名单引号修复

## 问题
Itinerary (ID 433) 等专辑封面文件名含单引号（如 `Jo's`），导致前端 URL 加载失败。

## 修复
- 批量重命名 covers/ 目录下所有含单引号的文件（移除单引号）
- 同步更新数据库 `cover_image_url` 字段
- 共修复 12 个文件（含 Itinerary）

## 修复清单
| ID | 原文件名 | 新文件名 |
|----|----------|----------|
| 433 | 433-Jo's Moving Day-Itinerary.jpg | 433-Jos-Moving-Day-Itinerary.jpg |
| 179 | 179-Oasis-(What's The Story)Morning Glory_.jpg | 179-Oasis-(Whats The Story)Morning Glory_.jpg |
| 183 | 183-Dissection-Storm of the Light's Bane .jpg | 183-Dissection-Storm of the Lights Bane .jpg |
| 199 | 199-Explosicum-Living's Deal.jpg | 199-Explosicum-Livings Deal.jpg |
| 231 | 231-The Beach Boys-Surf's Up.jpg | 231-The Beach Boys-Surfs Up.jpg |
| 249 | 249-Red Hot Chili Peppers-I'm With You.jpg | 249-Red Hot Chili Peppers-Im With You.jpg |
| 472 | 472-...-You Can't Eat It... | 472-...-You Cant Eat It... |
| 48 | 48-R.E.M.-Life's Rich Pageant.jpg | 48-R.E.M.-Lifes Rich Pageant.jpg |
| 488 | 488-Ratboys-Singin' to an Empty Chair.jpg | 488-Ratboys-Singin to an Empty Chair.jpg |
| 493 | 493-Mitski-Nothing's About to Happen to Me.jpg | 493-Mitski-Nothings About to Happen to Me.jpg |
| 497 | 497-You Are an Angel-It's Fine to Dream.jpg | 497-You Are an Angel-Its Fine to Dream.jpg |
| 506 | 506-The Twilight Sad-It's the Long Goodbye.jpg | 506-The Twilight Sad-Its the Long Goodbye.jpg |

## 后续
- 新专辑入库时封面文件名应避免特殊字符（单引号、括号等），用 `-` 替代
- Web 服务已重启
