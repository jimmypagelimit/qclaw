$path = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run'
$items = Get-ItemProperty -Path $path
$critical = @('OneDrive','QClaw','OpenClaw','OpenShell','Everything')
$removed = @()
foreach ($item in $items.PSObject.Properties) {
    $skip = $false
    $name = $item.Name
    foreach ($c in $critical) {
        if ($name -match $c) { $skip = $true; break }
    }
    if (-not $skip -and $name -notmatch '^PS') {
        Write-Host "Disabled: $name"
        Remove-ItemProperty -Path $path -Name $name
        $removed += $name
    }
}
if ($removed.Count -eq 0) {
    Write-Host "No startup items to disable (or all are critical)"
} else {
    Write-Host "Removed $($removed.Count) startup items"
}
