#!/bin/bash
cd /c/Users/qujt/.qclaw/workspace

# Stage changes
echo "=== Staging all ==="
git add -A 2>&1

echo ""
echo "=== Status after add ==="
git status --short 2>&1 | wc -l
echo " files staged"

# Commit
echo ""
echo "=== Committing ==="
git commit -m "2026-07-10: AF LP4 cover fix + debut album (1999)入库 + 近期专辑/收听记录维护" 2>&1

# Push
echo ""
echo "=== Pushing ==="
git push 2>&1
