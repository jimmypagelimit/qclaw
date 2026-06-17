@echo off
cd /d "C:\Users\qujt\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker"
taskkill /f /im node.exe >nul 2>&1
timeout /t 1 /nobreak >nul
echo Starting album-tracker server...
node dist/server.js
