#!/bin/bash
cd "C:/Users/qujt/.qclaw/workspace" || exit 1

# 初始化
git init

# 创建 .gitignore
cat > .gitignore << 'EOF'
node_modules/
dist/
*.log
.env
.DS_Store
Thumbs.db
tmp/
_cleaners_*.jpg
task-artifact_*.md
task-summary_*.md
EOF

# 添加所有文件（排除 gitignore 的）
git add .

# 首次提交
git commit -m "Initial commit: workspace setup (2026-05-22)

- Python 3.11 @ C:\Python311
- ffmpeg 8.1.1 @ C:\ffmpeg
- Everything HTTP @ localhost:18000
- album-tracker project
- MEMORY/TOOLS/USER/SOUL/AGENTS/HEARTBEAT
- skills/ RSS-SOURCES/ MEMORY-技术经验"

echo "=== Git init done ==="
git log --oneline -1
git status --short
