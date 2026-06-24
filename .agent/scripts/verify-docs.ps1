Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $root

$required = @(
    "docs\architecture\README.md",
    "docs\architecture\current-architecture.md",
    "docs\architecture\target-architecture.md",
    "docs\architecture\phases\README.md",
    "docs\architecture\programs\official-graphrag-cleanup-v1\README.md"
)

foreach ($path in $required) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Missing docs entrypoint: $path"
    }
}

$index = Get-Content -LiteralPath "docs\architecture\README.md" -Raw
if ($index -notmatch "official-graphrag-cleanup-v1") {
    throw "docs/architecture/README.md does not point to official-graphrag-cleanup-v1"
}
if ($index -notmatch "AGENTS.md") {
    throw "docs/architecture/README.md does not describe AGENTS.md boundary"
}
if ($index -notmatch "\.agent/") {
    throw "docs/architecture/README.md does not describe .agent boundary"
}

Write-Host "Docs verification passed."
