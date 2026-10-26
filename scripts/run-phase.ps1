# Starts Codex on one build phase.
# Usage: .\scripts\run-phase.ps1 -Phase 2 [-Exec]
#   default : opens Codex interactively with the phase prompt (recommended)
#   -Exec   : runs Codex non-interactively and exits when the phase is done

param(
    [Parameter(Mandatory = $true)]
    [ValidateRange(0, 8)]
    [int]$Phase,
    [switch]$Exec
)

$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot

if (-not (Get-Command codex -ErrorAction SilentlyContinue)) {
    Write-Error 'codex is not installed or not on PATH'
}

$file = Get-ChildItem -Path (Join-Path $root 'prompts') -Filter "phase-$Phase-*.md" | Select-Object -First 1
if (-not $file) {
    Write-Error "no prompt file found for phase $Phase"
}

Write-Host "Phase ${Phase}: $($file.Name)"
$prompt = Get-Content -Raw -Path $file.FullName

Set-Location $root
if ($Exec) {
    codex exec $prompt
} else {
    codex $prompt
}
