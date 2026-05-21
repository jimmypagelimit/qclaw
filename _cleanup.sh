#!/bin/bash
cd "C:/Users/qujt/.qclaw/workspace" || exit 1

# Remove temp files from git index
git rm --cached _init_git.sh .commit_msg.txt 2>/dev/null || true

# Also remove from disk if exists
rm -f _init_git.sh _do_commit.sh .commit_msg.txt

# Commit cleanup
git add -A
git commit -m "cleanup: remove temp init scripts from repo"

echo "=== Cleanup done ==="
git log --oneline -3
