import subprocess, sys

cmds = [
    # 12:00 独立/摇滚
    [
        "openclaw", "cron", "add",
        "--name", "translate-indie",
        "--cron", "0 12 * * *",
        "--tz", "Asia/Shanghai",
        "--message", "执行深度翻译(indie): 1)运行 C:\\Python311\\python.exe C:\\Users\\qujt\\.qclaw\\workspace\\_deep_translate.py --slot=indie 2)读取 C:\\Users\\qujt\\.qclaw\\workspace\\_translate_indie.json 3)对每篇文章full_text逐段中英对照翻译(格式:英文原文段落+空行+第N段+中文翻译+空行) 4)汇总发飞书,标题:🎸 独立/摇滚 深度翻译 | 日期 5)无重要更新则不发",
        "--session", "isolated",
        "--timeout-seconds", "300",
        "--announce",
        "--tools", "exec,read,write",
        "--thinking", "low",
    ],
    # 18:30 金属/极端
    [
        "openclaw", "cron", "add",
        "--name", "translate-metal",
        "--cron", "30 18 * * *",
        "--tz", "Asia/Shanghai",
        "--message", "执行深度翻译(metal): 1)运行 C:\\Python311\\python.exe C:\\Users\\qujt\\.qclaw\\workspace\\_deep_translate.py --slot=metal 2)读取 C:\\Users\\qujt\\.qclaw\\workspace\\_translate_metal.json 3)对每篇文章full_text逐段中英对照翻译(格式:英文原文段落+空行+第N段+中文翻译+空行) 4)汇总发飞书,标题:🔥 金属/极端 深度翻译 | 日期 5)无重要更新则不发",
        "--session", "isolated",
        "--timeout-seconds", "300",
        "--announce",
        "--tools", "exec,read,write",
        "--thinking", "low",
    ],
    # 22:00 民谣/前卫
    [
        "openclaw", "cron", "add",
        "--name", "translate-folk",
        "--cron", "0 22 * * *",
        "--tz", "Asia/Shanghai",
        "--message", "执行深度翻译(folk): 1)运行 C:\\Python311\\python.exe C:\\Users\\qujt\\.qclaw\\workspace\\_deep_translate.py --slot=folk 2)读取 C:\\Users\\qujt\\.qclaw\\workspace\\_translate_folk.json 3)对每篇文章full_text逐段中英对照翻译(格式:英文原文段落+空行+第N段+中文翻译+空行) 4)汇总发飞书,标题:🌊 民谣/前卫 深度翻译 | 日期 5)无重要更新则不发",
        "--session", "isolated",
        "--timeout-seconds", "300",
        "--announce",
        "--tools", "exec,read,write",
        "--thinking", "low",
    ],
]

for i, cmd in enumerate(cmds):
    print(f"Creating cron job {i+1}/3: {cmd[4]}...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, shell=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if result.returncode != 0:
        print(f"  ERROR: return code {result.returncode}")
    else:
        print(f"  OK")
