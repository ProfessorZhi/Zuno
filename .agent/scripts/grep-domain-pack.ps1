Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $root

$patterns = @(
    "Domain Pack",
    "domain_pack",
    "DomainQAGraph",
    "MultiAgentSupervisorGraph",
    "domain-packs"
)

$roots = @(
    "AGENTS.md",
    "README.md",
    ".agent",
    "docs",
    "tests",
    "tools",
    "src",
    "apps",
    "examples",
    "infra"
)

$rg = Get-Command "rg" -ErrorAction SilentlyContinue
if (-not $rg) {
    Write-Error "rg is required for this grep helper."
    exit 1
}

foreach ($pattern in $patterns) {
    Write-Host ""
    Write-Host "=== $pattern ==="
    & rg -n -F $pattern @roots -g "!docs/architecture/history/**"
    if ($LASTEXITCODE -gt 1) {
        exit $LASTEXITCODE
    }
}

exit 0
