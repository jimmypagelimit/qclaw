$feeds_indie = @(
    'https://pitchfork.com/feed/rss',
    'https://www.stereogum.com/feed/',
    'https://consequence.net/feed/',
    'https://post-punk.com/feed/',
    'https://aquariumdrunkard.com/feed/'
)

$feeds_metal = @(
    'https://www.decibelmagazine.com/feed/',
    'https://www.nocleansinging.com/feed/',
    'https://www.angrymetalguy.com/feed/',
    'https://www.invisibleoranges.com/feed/',
    'https://www.lambgoat.com/rss/news',
    'https://metalinjection.net/feed/'
)

$feeds_religion = @(
    'https://www.lionsroar.com/feed/',
    'https://www.christianitytoday.com/feed/',
    'https://www.religionnews.com/feed/',
    'https://www.islam21c.com/feed/',
    'https://www.forward.com/feed/'
)

$dayago = (Get-Date).AddDays(-1)
$allResults = @{}

function Get-RssRecent {
    param($urls, $label)
    $catItems = @()
    foreach ($url in $urls) {
        try {
            $items = Invoke-RestMethod -Uri $url -TimeoutSec 15 -UserAgent 'Mozilla/5.0' -ErrorAction SilentlyContinue
            if ($items -and $items.Count -gt 0) {
                $recent = $items | Where-Object { $_.pubDate -gt $dayago } | Select-Object -First 3
                foreach ($item in $recent) {
                    $title = "$($item.title)"
                    if ([string]::IsNullOrWhiteSpace($title)) { $title = "$($item.name)" }
                    $title = $title -replace '<[^>]+>', ''
                    $title = $title.Trim()
                    if ($title.Length -gt 90) { $title = $title.Substring(0, 87) + '...' }
                    $link = "$($item.link)"
                    $catItems += [PSCustomObject]@{Title=$title; Link=$link; Source=$label}
                }
            }
        } catch { }
    }
    return $catItems
}

Write-Output "INDIE_START"
$indie = Get-RssRecent $feeds_indie 'Indie'
if ($indie.Count -gt 0) {
    foreach ($i in $indie) { Write-Output "INDIE_ITEM:$($i.Title)|$($i.Link)" }
} else {
    Write-Output "INDIE_NONE"
}
Write-Output "INDIE_END"

Write-Output "METAL_START"
$metal = Get-RssRecent $feeds_metal 'Metal'
if ($metal.Count -gt 0) {
    foreach ($m in $metal) { Write-Output "METAL_ITEM:$($m.Title)|$($m.Link)" }
} else {
    Write-Output "METAL_NONE"
}
Write-Output "METAL_END"

Write-Output "RELIGION_START"
$religion = Get-RssRecent $feeds_religion 'Religion'
if ($religion.Count -gt 0) {
    foreach ($r in $religion) { Write-Output "RELIGION_ITEM:$($r.Title)|$($r.Link)" }
} else {
    Write-Output "RELIGION_NONE"
}
Write-Output "RELIGION_END"
