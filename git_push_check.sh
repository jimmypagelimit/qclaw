#!/bin/bash
cd /c/Users/qujt/.qclaw/workspace
echo "=== UNPUSHED COMMITS ==="
git log origin/main..HEAD --oneline 2>/dev/null || echo "No upstream or no new commits"
echo ""
echo "=== LAST COMMIT ==="
git log -1 --format="%h %ai %s"
