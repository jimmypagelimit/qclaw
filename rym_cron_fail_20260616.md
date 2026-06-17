# RYM评分回填任务失败报告

**执行时间：** 2026-06-16 02:00 (Asia/Shanghai)
**任务ID：** 45faa814-de36-492d-ad7b-d9c920e0f9f3
**命令：** `C:\Python311\python.exe C:\Users\qujt\.qclaw\workspace\rym_fill_v3.py --limit 20`

## 执行结果

- **成功：** 0 张专辑
- **失败：** 8 张专辑
- **失败原因：** 全部因为 Cloudflare Turnstile 挑战无法通过

## 失败的专辑

1. ����ŭ - Beyond (id=141)
2. Thick As A Brick - Jethro Tull (id=143)
3. Dragon New Warm Mountain I Believe in you - Big Thief (id=144)
4. Thriller - Michael Jackson (id=151)
5. Back In Black - AC/DC (id=153)
6. The Rise and Fall of Ziggy Stardust and the Spiders from Mars - David Bowie (id=156)
7. Master of Puppets - Metallica (id=161)
8. The Mantle - Agalloch (id=162)

## 根本原因分析

### CloakBrowser 无法通过 Cloudflare Turnstile 验证

**诊断步骤：**

1. **执行 `rym_fill_v3.py`**
   - 所有专辑都因为找不到搜索框 `#ui_search_input_main_search` 而跳过
   - 错误： `Locator.wait_for: Timeout 10000ms exceeded`

2. **手动测试 CloakBrowser**
   ```
   from cloakbrowser import launch
   browser = launch(headless=False)
   page = browser.new_page()
   page.goto('https://rateyourmusic.com', timeout=60000)
   time.sleep(40)
   ```
   - 页面标题乱码（`Ժ`）
   - HTML 长度只有 31691 字符（正常 RYM 页面应该 >100KB）
   - 搜索框 `#ui_search_input_main_search` 不存在

3. **检查页面内容**
   - 页面包含 Cloudflare 关键词
   - 有 2 个 frame：
     - 主页面：`https://rateyourmusic.com/`
     - **CF Turnstile iframe**：`https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/turnstile/...`
   - HTML 内容是 CF 挑战页面，不是真正的 RYM 页面

4. **测试原始 `rym_tool.py`**
   - 之前（2026-06-08）验证成功的脚本
   - 现在也失败，同样的错误：等待搜索框超时

### Cloudflare Turnstile 挑战

**Turnstile URL：**
```
https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/turnstile/f/ov2/av0/rch/8gq4v/0x4AAAAAAADnPIDROrmt1Wwj/light/fbE/new/normal?lang=auto
```

**特征：**
- "light" 模式（应该是自动完成的）
- 但等待 60 秒后仍未完成
- 可能是 "interactive" 模式（需要点击验证）

**可能原因：**
1. RYM 升级了 Cloudflare 保护（2026-06-08 后能过，现在不能）
2. 环境变化（QEMU 虚拟机被 CF 标记）
3. CloakBrowser/Playwright 被 CF 识别为自动化工具
4. 没有真实的显示器，headless=False 模式无法正确渲染/交互

## 解决方案

### 方案 1：使用 opencli + CDP（推荐）

TOOLS.md 中明确提到这是 **首选方案**：

**步骤：**
1. 手动启动 Chrome 远程调试：
   ```cmd
   start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --no-sandbox --remote-debugging-port=9222 --remote-allow-origins=*
   ```

2. 手动访问 `https://rateyourmusic.com` 并通过 CF 验证（在 Chrome 窗口中）

3. 修改 `rym_tool.py` 使用 opencli + CDP：
   ```bash
   opencli browser work bind          # 绑定到现有 Chrome
   opencli browser work open https://rateyourmusic.com/release/album/...
   opencli browser work extract       # 提取内容
   ```

4. 重写 `rym_fill_v3.py` 使用 opencli 而不是 CloakBrowser

**优点：**
- 复用已通过 CF 的 Chrome 会话（cookies/本地存储）
- CF 验证只需一次，后续请求都通过
- TOOLS.md 推荐方案

**缺点：**
- 需要手动启动 Chrome 远程调试
- 需要修改现有脚本

### 方案 2：等待 CF 挑战完成（不推荐）

在脚本中增加等待时间（120-300 秒），并模拟人工交互（鼠标移动、滚动）。

**测试结果：**
- 等待 60 秒 → 未完成
- 可能需要 5-10 分钟
- 成功率不确定

**不推荐原因：**
- Turnstile 可能永远不完成（如果检测为自动化）
- 每张专辑需要 5-10 分钟，20 张专辑需要 2-3 小时

### 方案 3：使用替代数据源

**AnyDecentMusic API：**
- 无 Cloudflare 保护
- 有加权评分（聚合多个数据源）
- 但可能没有 RYM 的详细评分/评价数

**手动导入：**
- 从 RYM 手动导出评分数据
- 导入到 `_music_latest.db`

**缺点：**
- 需要手动操作
- 数据可能不完整

### 方案 4：暂时停止 cron 任务

如果暂时无法修复，应该停止 cron 任务，防止每天失败。

**命令：**
```
/cron delete 45faa814-de36-492d-ad7b-d9c920e0f9f3
```

## 建议行动

1. **立即：** 停止 cron 任务（防止每天失败）
2. **短期：** 手动启动 Chrome 远程调试，测试 opencli + CDP 方案
3. **长期：** 重写 `rym_tool.py` 和 `rym_fill_v3.py` 使用 opencli + CDP

## 附加信息

**环境：**
- QEMU 虚拟机（所有自行启动浏览器的方案都被 SIGKILL 杀死）
- Windows 10 (10.0.19045)
- Python 3.11
- CloakBrowser (基于 Playwright)

**相关文件：**
- `rym_fill_v3.py` - 批量回填脚本（失败）
- `rym_tool.py` - 单张专辑查询脚本（也失败）
- `TOOLS.md` - 包含 opencli + CDP 方案说明

**历史记录：**
- 2026-06-08：原始 `rym_tool.py` 测试成功（Car Seat Headrest, The Cure, Sonic Youth, Paul McCartney）
- 2026-06-16：同样脚本失败（CF Turnstile 无法通过）

---

**结论：** RYM 的 Cloudflare 保护已升级，CloakBrowser 方案不再可用。需要切换到 opencli + CDP 方案。
