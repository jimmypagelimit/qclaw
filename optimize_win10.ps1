# Windows 10 极致性能优化脚本
$ErrorActionPreference = "SilentlyContinue"

Write-Host "=== 开始性能优化 ==="

# 1. 界面渲染优化 - 关闭视觉特效
Write-Host "[1/5] 关闭视觉特效..."
Set-ItemProperty -Path "HKCU:\Control Panel\Desktop" -Name "MenuShowDelay" -Value 0
Set-ItemProperty -Path "HKCU:\Control Panel\Desktop" -Name "MouseHoverTime" -Value 0
Set-ItemProperty -Path "HKCU:\Control Panel\Desktop" -Name "UserPreferencesMask" -Value ([byte[]](0x9E,0x1E,0x07,0x80,0x12,0x00,0x00,0x00))
Set-ItemProperty -Path "HKCU:\Control Panel\Desktop" -Name "DragFullWindows" -Value 0
Set-ItemProperty -Path "HKCU:\Control Panel\Desktop" -Name "FontSmoothing" -Value 2
Write-Host "  ✓ 视觉特效已禁用"

# 2. 禁用非必要服务
Write-Host "[2/5] 禁用非必要服务..."
$services = @{
    "Spooler" = "Print Spooler"
    "WSearch" = "Windows Search"
    "SysMain" = "SysMain (Superfetch)"
    "DiagTrack" = "Telemetry"
}
foreach ($svc in $services.Keys) {
    $status = (Get-Service -Name $svc -ErrorAction SilentlyContinue).StartType
    if ($status -ne "Disabled") {
        Set-Service -Name $svc -StartupType Disabled
        Write-Host "  ✓ $($services[$svc]) 已禁用 (原: $status)"
    } else {
        Write-Host "  - $($services[$svc]) 已禁用"
    }
}

# 3. 电源计划 - 高性能
Write-Host "[3/5] 设置电源计划..."
try {
    $highPerf = powercfg -list | Select-String "高性能"
    if (-not $highPerf) {
        powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61 2>$null
    }
    powercfg -setactive SCHEME_MIN
    Write-Host "  ✓ 已切换到高性能模式"
} catch {
    Write-Host "  ! 电源计划设置失败"
}

# 4. 关闭后台应用
Write-Host "[4/5] 关闭后台应用..."
$bgApps = Get-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications" -ErrorAction SilentlyContinue
if ($bgApps) {
    foreach ($app in $bgApps.PSObject.Properties) {
        if ($app.Name -match "UserConfigurable" -or $app.Name -match "GlobalUserEnabled") {
            Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications" -Name $app.Name -Value 0
        }
    }
}
Write-Host "  ✓ 后台应用已限制"

# 5. 清理启动项
Write-Host "[5/5] 禁用非必要启动项..."
$startupPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
$startupItems = Get-ItemProperty -Path $startupPath -ErrorAction SilentlyContinue
$disabledCount = 0
if ($startupItems) {
    $critical = @("OneDrive", "OpenShell", "OpenShell64", "QClaw", "OpenClaw")
    foreach ($item in $startupItems.PSObject.Properties) {
        $isCritical = $false
        foreach ($c in $critical) {
            if ($item.Name -match $c) { $isCritical = $true; break }
        }
        if (-not $isCritical -and $item.Name -ne "PSPath" -and $item.Name -ne "PSParentPath" -and $item.Name -ne "PSChildName" -and $item.Name -ne "PSDrive" -and $item.Name -ne "PSProvider") {
            Remove-ItemProperty -Path $startupPath -Name $item.Name
            Write-Host "  ✓ 已禁用启动项: $($item.Name)"
            $disabledCount++
        }
    }
}
if ($disabledCount -eq 0) {
    Write-Host "  - 无需禁用 (可能已清理)"
}

Write-Host ""
Write-Host "=== 优化完成 ==="
Write-Host "请重启电脑使所有更改生效。"
