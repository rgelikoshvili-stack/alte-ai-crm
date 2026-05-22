$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$PackageName = "alte-ai-crm-v0.7-local-mvp.zip"
$PackagePath = Join-Path $Root $PackageName
$TempPath = Join-Path ([System.IO.Path]::GetTempPath()) ("alte-ai-crm-package-" + [System.Guid]::NewGuid())

if (Test-Path $PackagePath) {
    Remove-Item -LiteralPath $PackagePath -Force
}

New-Item -ItemType Directory -Path $TempPath | Out-Null

try {
    $Destination = Join-Path $TempPath "alte-ai-crm"
    New-Item -ItemType Directory -Path $Destination | Out-Null

    Get-ChildItem -LiteralPath $Root -Force | Where-Object {
        $_.Name -notin @(".git", ".venv", ".pytest_cache", "__pycache__", ".env", $PackageName) -and
        $_.Name -notmatch "\.(db|sqlite|sqlite3|log)$"
    } | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $Destination -Recurse -Force
    }

    Get-ChildItem -LiteralPath $Destination -Recurse -Force | Where-Object {
        $_.FullName -match "\\(__pycache__|\.pytest_cache|\.venv)(\\|$)" -or
        $_.Name -eq ".env" -or
        $_.Name -match "\.(db|sqlite|sqlite3|log|pyc)$"
    } | Remove-Item -Force -Recurse

    Compress-Archive -Path (Join-Path $Destination "*") -DestinationPath $PackagePath -Force
    Write-Host "Package created: $PackagePath"
}
finally {
    if (Test-Path $TempPath) {
        Remove-Item -LiteralPath $TempPath -Recurse -Force
    }
}
