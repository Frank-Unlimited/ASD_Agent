$body = @{
    group_id = "child_chenchen_001"
    content = "辰辰在积木游戏中表现出3次主动眼神接触，互动积极性提升"
    reference_time = "2026-06-15T10:30:00+08:00"
} | ConvertTo-Json -Compress

$bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($body)

Write-Host "=== Testing WRITE ==="
try {
    $resp = Invoke-WebRequest -Uri http://localhost:8000/api/memory/write -Method POST -Body $bodyBytes -ContentType "application/json; charset=utf-8" -UseBasicParsing
    Write-Host "Status: $($resp.StatusCode)"
    Write-Host "Response: $($resp.Content)"
} catch {
    Write-Host "Error: $_"
}

Write-Host ""
Write-Host "=== Waiting 5 seconds for processing ==="
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "=== Testing SEARCH ==="
$searchBody = @{
    group_id = "child_chenchen_001"
    query = "眼神接触"
    num_results = 5
} | ConvertTo-Json -Compress

$searchBodyBytes = [System.Text.Encoding]::UTF8.GetBytes($searchBody)

try {
    $resp2 = Invoke-WebRequest -Uri http://localhost:8000/api/memory/search -Method POST -Body $searchBodyBytes -ContentType "application/json; charset=utf-8" -UseBasicParsing
    Write-Host "Status: $($resp2.StatusCode)"
    Write-Host "Response: $($resp2.Content)"
} catch {
    Write-Host "Error: $_"
}
