param(
    [string]$BackendUrl = 'http://localhost:8002/exam-assistant/health',
    [string]$FrontendUrl = 'http://localhost:5173'
)

$ErrorActionPreference = 'Stop'

$Failures = 0

function Write-Ok($Message) {
    Write-Host "[ok] $Message"
}

function Write-Fail($Message) {
    Write-Host "[fail] $Message"
    $script:Failures++
}

Write-Host 'Workshop app healthcheck'
Write-Host ''

try {
    $BackendResponse = Invoke-RestMethod -Uri $BackendUrl -Method Get -TimeoutSec 10
    Write-Ok "Backend reachable at $BackendUrl"
    Write-Host "      response: $($BackendResponse | ConvertTo-Json -Compress)"
} catch {
    Write-Fail "Backend not reachable at $BackendUrl"
}

try {
    Invoke-WebRequest -Uri $FrontendUrl -Method Get -TimeoutSec 10 | Out-Null
    Write-Ok "Frontend reachable at $FrontendUrl"
} catch {
    Write-Fail "Frontend not reachable at $FrontendUrl"
}

Write-Host ''
if ($Failures -eq 0) {
    Write-Host 'Healthcheck passed.'
    Write-Host 'Suggested smoke test: upload resources/documents/CPU.md and ask a question in the browser.'
    exit 0
}

Write-Host "Healthcheck failed with $Failures issue(s)."
exit 1
