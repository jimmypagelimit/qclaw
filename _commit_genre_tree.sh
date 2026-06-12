#!/bin/bash
cd C:/Users/qujt/.qclaw/workspace/tasks/rym-expert
git add scripts/fetch_genre_tree_recursive.py data/genres/*_tree*.json
git commit -m "RYM 流派树递归抓取脚本（实测2层结构，rock 63子流派）"
git push
