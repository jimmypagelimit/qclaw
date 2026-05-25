Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Name -in 'H','G','C' } | ForEach-Object {
    $n=$_.Name
    $u=[math]::Round($_.Used/1GB,1)
    $f=[math]::Round($_.Free/1GB,1)
    Write-Output "Drive $n`: Used=$u GB Free=$f GB"
}