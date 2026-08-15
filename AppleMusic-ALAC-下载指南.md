# Apple Music ALAC 下载器使用指南

## 概述

通过 Docker 运行 wrapper-manager，配合 AppleMusicDecrypt 从 Apple Music 下载 ALAC 无损音频。

- **wrapper-manager**: 管理 wrapper 实例，处理 FairPlay DRM 解密
- **AppleMusicDecrypt**: Python 客户端，调用 wrapper-manager 下载并保存音频
- **需要**: Apple Music 订阅账号

## 架构

```
AppleMusicDecrypt (Python) → gRPC:8080 → wrapper-manager (Docker)
                                              ↓
                                          wrapper 实例
                                              ↓
                                          Apple Music API (用你的订阅解密)
```

---

## 一、启动 wrapper-manager

### 1. 确认 Docker 运行中

```bash
systemctl status docker
# 如果没运行：
systemctl start docker
```

### 2. 启动 wrapper-manager 容器

```bash
docker run -d \
  --name wrapper-manager \
  --restart unless-stopped \
  --privileged \
  -p 8080:8080 \
  wrapper-manager:x86_64 \
  --host 0.0.0.0 --port 8080
```

### 3. 验证运行状态

```bash
# 查看容器状态
docker ps | grep wrapper-manager

# 查看日志
docker logs wrapper-manager 2>&1 | tail -5

# 应该看到：
# wrapperManager running at 0.0.0.0:8080
```

### 4. 检查 wrapper 二进制架构（必须是 x86_64）

```bash
docker exec wrapper-manager sh -c "/root/data/wrapper/wrapper --version"
# 应该输出: wrapper 1.2.0
```

---

## 二、登录 Apple ID

### 1. 进入 AppleMusicDecrypt 目录

```bash
cd /root/AppleMusicDecrypt
export PATH="$HOME/.local/bin:$PATH"
```

### 2. 运行登录脚本

```bash
poetry run python tools/login.py
```

### 3. 按提示输入

```
Username: 你的AppleID@xxx.com
Password: 你的密码
2FA code: 6位验证码（从你的iPhone/Mac获取）
```

**获取 2FA 验证码的方法**：
- **iPhone**: 设置 → Apple ID → 密码与安全性 → 获取验证码
- **Mac**: 系统设置 → Apple ID → 密码与安全性 → 获取验证码
- 或者设备上直接弹出的通知，点"允许"

### 4. 登录成功标志

```
Login Success!
```

### 5. 如果登录失败

- **"Forgot Your Password?"** → Apple 账号被锁定，等 15-30 分钟后重试
- **2FA 收不到** → 检查 Apple ID 受信任设备列表
- **Connection refused** → wrapper-manager 未启动，回到第一步

---

## 三、使用方法

### 1. 启动交互式命令行

```bash
cd /root/AppleMusicDecrypt
export PATH="$HOME/.local/bin:$PATH"
poetry run python main.py
```

进入后显示 `>` 提示符。

### 2. 下载专辑（ALAC 无损）

```
> dl https://music.apple.com/us/album/专辑名/专辑ID
```

示例：
```
> dl https://music.apple.com/us/album/teen-of-denial/6764628009
```

### 3. 下载单曲

```
> dl https://music.apple.com/us/song/歌曲名/歌曲ID
```

### 4. 指定编码格式

```
> dl -c alac https://music.apple.com/us/album/xxx/xxx    # ALAC 无损（默认）
> dl -c aac https://music.apple.com/us/album/xxx/xxx     # AAC 256kbps
> dl -c ec3 https://music.apple.com/us/album/xxx/xxx     # Dolby Atmos
```

### 5. 下载播放列表

```
> dl https://music.apple.com/us/playlist/播放列表名/播放列表ID
```

### 6. 检查可用音质

```
> qa https://music.apple.com/us/album/xxx/xxx
```

### 7. 退出

```
> exit
```

---

## 四、下载文件位置

默认保存路径：`/root/Music/{艺术家}/{专辑名}/`

```
/root/Music/
├── Car Seat Headrest/
│   └── Teen of Denial Joe's Story/
│       ├── 1-01 Fill In The Blank.m4a   # ALAC 音频
│       ├── 1-01 Fill In The Blank.lrc   # 歌词
│       └── cover.jpg                     # 封面
└── ...
```

可在 `/root/AppleMusicDecrypt/config.toml` 中修改保存路径：

```toml
[download]
dirPathFormat = "/root/Music/{album_artist}/{album}"
```

---

## 五、配置文件说明

位置：`/root/AppleMusicDecrypt/config.toml`

```toml
[instance]
url = "127.0.0.1:8080"    # wrapper-manager 地址（本地 Docker）
secure = false              # 本地不需要 HTTPS

[region]
language = "en-US"          # 元数据语言（可改 zh-Hans-CN 中文）

[download]
parallelNum = 2             # 并行下载数
maxRunningTasks = 4         # 最大任务数
codecPriority = ["alac", "aac"]  # 编码优先级
saveLyrics = true           # 保存歌词
saveCover = true            # 保存封面
coverSize = "5000x5000"    # 封面分辨率
```

---

## 六、常见问题

### Q: SSL 连接错误
```
[SSL: UNEXPECTED_EOF_WHILE_READING]
```
**A**: Apple CDN 间歇性问题，重试一次就好。第二次几乎必定成功。

### Q: 歌曲下载超时
```
Task processing timed out or was cancelled
```
**A**: 网络问题或 wrapper 连接不稳定。重启 wrapper-manager 后重试：
```bash
docker restart wrapper-manager
```

### Q: 404 错误
```
Resource Not Found
```
**A**: 专辑/歌曲 ID 错误或已下架。检查 URL 是否正确。

### Q: wrapper-manager 崩溃重启
```bash
docker logs wrapper-manager 2>&1 | tail -10
# 如果是 "exec format error"，说明 wrapper 二进制架构错误
# 需要重新部署（见下方"重建环境"）
```

### Q: 登录后 token 过期
重新运行登录脚本：
```bash
cd /root/AppleMusicDecrypt
poetry run python tools/login.py
```

---

## 七、日常操作速查

```bash
# 启动 wrapper-manager
docker start wrapper-manager

# 停止 wrapper-manager
docker stop wrapper-manager

# 查看日志
docker logs -f wrapper-manager

# 登录 Apple ID
cd /root/AppleMusicDecrypt && poetry run python tools/login.py

# 下载专辑
cd /root/AppleMusicDecrypt && poetry run python main.py
> dl https://music.apple.com/us/album/xxx/xxx

# 查看已下载文件
ls -lh /root/Music/
```

---

## 八、重建环境（如果 wrapper-manager 损坏）

```bash
# 1. 删除旧容器
docker stop wrapper-manager && docker rm wrapper-manager

# 2. 重新构建镜像（需要 wrapper-x86_64 源码在 /root/wrapper-manager/）
cd /root/wrapper-manager && docker build -f Dockerfile.custom -t wrapper-manager:x86_64 .

# 3. 重新启动
docker run -d --name wrapper-manager --restart unless-stopped --privileged \
  -p 8080:8080 wrapper-manager:x86_64 --host 0.0.0.0 --port 8080

# 4. 重新登录
cd /root/AppleMusicDecrypt && poetry run python tools/login.py
```

---

## 九、技术细节

- **wrapper-manager 版本**: 基于 WorldObservationLog/wrapper-manager
- **wrapper 版本**: 1.2.0 (x86_64)
- **AppleMusicDecrypt 版本**: v2 分支
- **Docker 镜像**: wrapper-manager:x86_64（内置 x86_64 wrapper 二进制）
- **gRPC 端口**: 8080
- **数据卷**: wrapper-manager-data（Docker volume）

---

*最后更新: 2026-08-14*
