# Chay public v6 sim qua Docker (LLM that). Yeu cau: Docker Desktop dang chay + .env co OPENAI_API_KEY.
#   .\run_public.ps1            # phase mac dinh = public
#   .\run_public.ps1 private    # chay private
param([string]$Phase = "public")
$ErrorActionPreference = "Stop"

Get-Content .env | ForEach-Object {
    if ($_ -match '^\s*OPENAI_API_KEY\s*=\s*(.+)$') { $env:OPENAI_API_KEY = $matches[1].Trim().Trim('"').Trim("'") }
}
if (-not $env:OPENAI_API_KEY) { Write-Error "Thieu OPENAI_API_KEY trong .env"; exit 1 }
if (-not (Test-Path "bin/$Phase/observathon-sim")) { Write-Error "Chua co bin/$Phase/observathon-sim (ban Linux ELF, khong .exe)"; exit 1 }

docker run --rm -e OPENAI_API_KEY -v "${PWD}:/lab" python:3.12-slim `
  bash -c "cd /lab && chmod +x bin/$Phase/observathon-sim && ./bin/$Phase/observathon-sim --config solution/config.json --wrapper solution/wrapper.py --out run_output.json --concurrency 8"
