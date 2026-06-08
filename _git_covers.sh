cd /c/Users/qujt/.qclaw/workspace/tasks/2026-05-12-long-term-project/album-tracker
git add database.sql public/covers/ _music_latest.db
git commit -m "Covers: +18 iTunes downloads, 9 failed (too obscure)"
cd /c/Users/qujt/.qclaw/workspace
git add _music_latest.db tasks/2026-05-12-long-term-project/album-tracker/database.sql
git commit -m "DB sync: covers update"
git push
