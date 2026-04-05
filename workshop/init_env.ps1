$ErrorActionPreference = 'Stop'

$ProjectDir = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Template = Join-Path $ProjectDir '.env.template'
$Target = Join-Path $ProjectDir '.env'

if (-not (Test-Path $Template)) {
    Write-Error "Missing template file: $Template"
}

if (Test-Path $Target) {
    Write-Host ".env already exists at $Target"
    Write-Host 'Leaving it unchanged.'
    exit 0
}

Copy-Item $Template $Target
Write-Host 'Created .env from .env.template'
Write-Host 'Next: edit .env and set OPENAI_API_KEY'
