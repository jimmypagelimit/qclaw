# C盘空间检查
$drive = Get-PSDrive C
$free = [math]::Round($drive.Free/1GB, 1)
$used = [math]::Round($drive.Used/1GB, 1)
Write-Host "C盘已用: $used GB, 剩余: $free GB"

# heartbeat-state.json 读取
$stateFile = Join-Path $env:USERPROFILE ".qclaw\workspace\heartbeat-state.json"
if (Test-Path $stateFile) {
    $content = Get-Content $stateFile -Raw
    Write-Host "State: $content"
} else {
    Write-Host "No state file"
}
