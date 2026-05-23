Write-Host "Alte AI CRM local secret value preparation"
Write-Host ""
Write-Host "Safety warnings:"
Write-Host "- Do not commit generated secrets."
Write-Host "- Do not paste secrets into chat, docs, GitHub, screenshots, or prompts."
Write-Host "- Store generated values only in a password manager and later in Secret Manager."
Write-Host "- This script does not call gcloud and does not create cloud resources."
Write-Host "- This script never asks for or prints ANTHROPIC_API_KEY."
Write-Host ""

$secretDir = Join-Path (Get-Location) ".local-secrets"
$secretFile = Join-Path $secretDir "secret-values.local.txt"

$bytes = New-Object byte[] 36
[System.Security.Cryptography.RandomNumberGenerator]::Fill($bytes)
$dbPassword = [Convert]::ToBase64String($bytes).TrimEnd("=").Replace("+", "A").Replace("/", "B")

$jwtBytes = New-Object byte[] 48
[System.Security.Cryptography.RandomNumberGenerator]::Fill($jwtBytes)
$jwtSecret = [Convert]::ToBase64String($jwtBytes)

Write-Host "Generated local DB password and JWT secret in memory."
Write-Host "The Anthropic API key must be handled separately and is not requested here."
Write-Host ""
Write-Host "Save generated values to .local-secrets/secret-values.local.txt?"
Write-Host "This path is ignored by Git, but still contains sensitive local values."
$answer = Read-Host "Type YES to save locally, anything else to skip"

if ($answer -eq "YES") {
    if (-not (Test-Path $secretDir)) {
        New-Item -ItemType Directory -Path $secretDir | Out-Null
    }

    $content = @(
        "# Alte AI CRM local secret values"
        "# Sensitive local file. Do not commit. Do not share."
        "alte-db-password=$dbPassword"
        "alte-jwt-secret=$jwtSecret"
        "alte-anthropic-api-key=PASTE_MANUALLY_IN_SECRET_MANAGER_ONLY_DO_NOT_COMMIT"
        "alte-database-url=PENDING_CLOUD_SQL_CREATION"
    )

    Set-Content -LiteralPath $secretFile -Value $content -Encoding UTF8
    Write-Host "Saved local secret preparation file:"
    Write-Host $secretFile
    Write-Host "Move values to a password manager or Secret Manager during the approved execution phase."
} else {
    Write-Host "Skipped saving generated values."
    Write-Host "Use a password manager or rerun this script when ready."
}
