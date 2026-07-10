#!/bin/bash
cd /c/Users/qujt/.qclaw/workspace
echo "=== GIT LOG last 5 ==="
git log --oneline -5
echo ""
echo "=== STATUS ==="
git status --short
echo ""
echo "=== BRANCH ==="
git rev-parse --abbrev-ref HEAD
echo ""
echo "=== AHEAD-BEHIND ==="
git status -sb
