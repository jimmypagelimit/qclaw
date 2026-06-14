Get-PSDrive C, H | ForEach-Object {
    $used = [math]::Round($_.Used/1GB, 1)
    $free = [math]::Round($_.Free/1GB, 1)
    Write-Output "$($_.Name): Used=$used GB, Free=$free GB"
}