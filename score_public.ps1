# Cham diem qua Docker. Chay SAU khi tai observathon-score (Linux ELF) ve bin/<phase>/.
#   .\score_public.ps1            # phase mac dinh = public
#   .\score_public.ps1 private
param([string]$Phase = "public")
$ErrorActionPreference = "Stop"
$TEAM = "solo858-team-name"     # khop solution/findings.json + submission/manifest.json

if (-not (Test-Path "bin/$Phase/observathon-score")) {
    Write-Error "Chua co bin/$Phase/observathon-score - tai ve roi chay lai."; exit 1
}
if (-not (Test-Path "run_output.json")) { Write-Error "Chua co run_output.json - chay .\run_public.ps1 truoc."; exit 1 }

Get-Content .env | ForEach-Object {
    if ($_ -match '^\s*OPENAI_API_KEY\s*=\s*(.+)$') { $env:OPENAI_API_KEY = $matches[1].Trim().Trim('"').Trim("'") }
}

docker run --rm -e OPENAI_API_KEY -v "${PWD}:/lab" python:3.12-slim `
  bash -c "cd /lab && chmod +x bin/$Phase/observathon-score && ./bin/$Phase/observathon-score --run run_output.json --findings solution/findings.json --team $TEAM --out score.json"

if (Test-Path score.json) { Write-Host "`n=== score.json ===" ; Get-Content score.json }
