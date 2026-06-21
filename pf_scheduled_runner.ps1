# pf_scheduled_runner.ps1 - Windows Scheduled Task runner
# Runs pf_batch_fill_v2.py with small batch size

$scriptDir = "C:\Users\qujt\.qclaw\workspace"
$pythonExe = "C:\Python311\python.exe"
$script = Join-Path $scriptDir "pf_batch_fill_v2.py"
$log = Join-Path $scriptDir "pf_scheduled.log"

$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
"[${timestamp}] Scheduled task triggered" | Out-File -FilePath $log -Append -Encoding UTF8

# Run batch with limit 10
$args = @($script, "--resume", "--limit", "10")
$result = & $pythonExe $args 2>&1
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
"[${timestamp}] Batch completed" | Out-File -FilePath $log -Append -Encoding UTF8
$result | Out-File -FilePath $log -Append -Encoding UTF8

# Check if more albums remain
$progressFile = Join-Path $scriptDir "pf_batch_progress.json"
if (Test-Path $progressFile) {
    $progress = Get-Content $progressFile | ConvertFrom-Json
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "[${timestamp}] Total processed so far: $($progress.Count)" | Out-File -FilePath $log -Append -Encoding UTF8
}
