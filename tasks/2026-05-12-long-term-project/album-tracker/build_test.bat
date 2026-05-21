@echo off
cd /d C:\Users\15206\.qclaw\workspace\tasks\2026-05-12-long-term-project\album-tracker
node scripts\build.js
if errorlevel 1 exit /b 1
node dist\cli.js info -i 124
