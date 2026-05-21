@echo off
setlocal enabledelayedexpansion

set "TMP_DIR=%TEMP%\skillhub_install"
if exist "%TMP_DIR%" rmdir /s /q "%TMP_DIR%"
mkdir "%TMP_DIR%"

echo Downloading Skillhub kit...
powershell -Command "Invoke-WebRequest -Uri 'https://skillhub-1388575217.cos.ap-guangzhou.myqcloud.com/install/latest.tar.gz' -OutFile '%TMP_DIR%\latest.tar.gz'"

echo Extracting...
powershell -Command "Expand-Archive -Path '%TMP_DIR%\latest.tar.gz' -DestinationPath '%TMP_DIR%' -Force"

if not exist "%TMP_DIR%\cli\install.bat" (
    echo Error: install.bat not found
    dir /s /b "%TMP_DIR%"
    exit /b 1
)

echo Running installer...
call "%TMP_DIR%\cli\install.bat"

echo Cleaning up...
rmdir /s /q "%TMP_DIR%"

echo Done!
