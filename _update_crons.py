import subprocess

edits = [
    {
        "id": "bf8c27ad-75c8-4d75-ac1c-c5aa969435f9",
        "msg": "执行深度翻译(indie): 1)运行 C:\\Python311\\python.exe C:\\Users\\qujt\\.qclaw\\workspace\\_deep_translate.py --slot=indie 2)读取 C:\\Users\\qujt\\.qclaw\\workspace\\_translate_indie.json 3)对每篇文章full_text逐段中英对照翻译(格式:英文原文段落+空行+第N段+中文翻译+空行) 4)翻译完成后保存到P项目: 英文原文存 C:\\Users\\qujt\\.qclaw\\workspace\\tasks\\pitchfork-expert\\docs\\en\\indie\\日期-源站-标题slug.md 中英对照存 C:\\Users\\qujt\\.qclaw\\workspace\\tasks\\pitchfork-expert\\docs\\zh\\indie\\日期-源站-标题slug.md 5)汇总发飞书 标题:🎸 独立/摇滚/民谣 深度翻译 | 日期 6)无重要更新则不发"
    },
    {
        "id": "0fd3f61c-ba21-40c4-8789-f0ee6151b105",
        "msg": "执行深度翻译(metal): 1)运行 C:\\Python311\\python.exe C:\\Users\\qujt\\.qclaw\\workspace\\_deep_translate.py --slot=metal 2)读取 C:\\Users\\qujt\\.qclaw\\workspace\\_translate_metal.json 3)对每篇文章full_text逐段中英对照翻译(格式:英文原文段落+空行+第N段+中文翻译+空行) 4)翻译完成后保存到P项目: 英文原文存 C:\\Users\\qujt\\.qclaw\\workspace\\tasks\\pitchfork-expert\\docs\\en\\metal\\日期-源站-标题slug.md 中英对照存 C:\\Users\\qujt\\.qclaw\\workspace\\tasks\\pitchfork-expert\\docs\\zh\\metal\\日期-源站-标题slug.md 5)汇总发飞书 标题:🔥 金属/硬核 深度翻译 | 日期 6)无重要更新则不发"
    },
    {
        "id": "54b9c3f9-bcf3-4dd4-8388-e874da35c304",
        "msg": "执行深度翻译(folk): 1)运行 C:\\Python311\\python.exe C:\\Users\\qujt\\.qclaw\\workspace\\_deep_translate.py --slot=folk 2)读取 C:\\Users\\qujt\\.qclaw\\workspace\\_translate_folk.json 3)对每篇文章full_text逐段中英对照翻译(格式:英文原文段落+空行+第N段+中文翻译+空行) 4)翻译完成后保存到P项目: 英文原文存 C:\\Users\\qujt\\.qclaw\\workspace\\tasks\\pitchfork-expert\\docs\\en\\folk\\日期-源站-标题slug.md 中英对照存 C:\\Users\\qujt\\.qclaw\\workspace\\tasks\\pitchfork-expert\\docs\\zh\\folk\\日期-源站-标题slug.md 5)汇总发飞书 标题:🌊 实验/地下 深度翻译 | 日期 6)无重要更新则不发"
    }
]

for e in edits:
    cmd = ["openclaw", "cron", "edit", e["id"], "--message", e["msg"]]
    print(f"Updating {e['id'][:8]}...")
    r = subprocess.run(cmd, capture_output=True, timeout=30, shell=True)
    if b'"enabled": true' in r.stdout or b'"name"' in r.stdout:
        print("  OK")
    else:
        print(f"  stdout: {r.stdout[:150]}")
