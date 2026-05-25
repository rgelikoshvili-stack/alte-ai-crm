param(
  [Parameter(Mandatory = $true)]
  [string]$TestOriginUrl
)

$ErrorActionPreference = "Stop"

Write-Host "STOP: Do not run without approval."
Write-Host "This template is for Phase 9N temporary test-origin CORS only."

if ([string]::IsNullOrWhiteSpace($TestOriginUrl)) {
  throw "TestOriginUrl is required."
}

if (-not $TestOriginUrl.StartsWith("https://", [System.StringComparison]::OrdinalIgnoreCase)) {
  throw "TestOriginUrl must start with https://"
}

if ($TestOriginUrl.Contains("*")) {
  throw "Wildcard origins are not allowed."
}

$ExistingOrigins = @(
  "https://alte.edu.ge",
  "https://join.alte.edu.ge"
)

$AllOrigins = @($ExistingOrigins + $TestOriginUrl) | Select-Object -Unique
$CorsOrigins = [string]::Join(",", $AllOrigins)

Write-Host "Planned temporary test origin:"
Write-Host $TestOriginUrl
Write-Host "Planned CORS origins:"
Write-Host $CorsOrigins

Write-Host "Before executing any Cloud Run update, confirm:"
Write-Host "- production CORS change is approved"
Write-Host "- Cloud Run redeploy is approved"
Write-Host "- existing env vars, Secret Manager mappings, and Cloud SQL attachment are preserved"
Write-Host "- no secrets are printed"

# Manual command pattern only. Review current service config before running.
# gcloud run deploy alte-ai-crm-backend `
#   --region europe-west1 `
#   --platform managed `
#   --update-env-vars CORS_ORIGINS=$CorsOrigins
