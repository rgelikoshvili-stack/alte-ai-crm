param(
    [int]$Port = 5173
)

$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$FrontendDir = Join-Path $RepoRoot "frontend"
$IndexFile = Join-Path $FrontendDir "index.html"

if (-not (Test-Path -LiteralPath $IndexFile)) {
    throw "Operator UI entrypoint not found: frontend/index.html"
}

Write-Host "Starting ALTE Operator CRM UI"
Write-Host "URL: http://127.0.0.1:$Port"
Write-Host "Folder: frontend"

Set-Location -LiteralPath $FrontendDir
python -m http.server $Port --bind 127.0.0.1
