$ErrorActionPreference = "Stop"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker is not installed or not available in PATH."
}

$root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $root

docker build -t alte-ai-crm-backend:local ./backend

Write-Host ""
Write-Host "Docker image built: alte-ai-crm-backend:local"
Write-Host "Next local run command:"
Write-Host "docker run --env-file backend/.env.local.example -p 8080:8080 alte-ai-crm-backend:local"
