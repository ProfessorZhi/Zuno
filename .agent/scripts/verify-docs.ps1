Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $root

$required = @(
    "docs\architecture\README.md",
    "docs\architecture\architecture.md",
    "docs\status\production-readiness.md",
    "docs\architecture\architecture.html",
    "docs\history\architecture-surface-cleanup-2026-06-30\docs-architecture\current-architecture.md",
    "docs\history\architecture-surface-cleanup-2026-06-30\docs-architecture\target-architecture.md",
    "docs\history\architecture-surface-cleanup-2026-06-30\docs-architecture\roadmap.md",
    "docs\history\architecture-surface-cleanup-2026-06-30\docs-architecture\deliverables.md",
    "docs\history\programs\zuno-target-architecture-runtime-full-implementation-v1\closure-summary.md"
)

foreach ($path in $required) {
    if (-not (Test-Path -LiteralPath $path)) {
        throw "Missing docs entrypoint: $path"
    }
}

$index = Get-Content -LiteralPath "docs\architecture\README.md" -Raw
if ($index -notmatch "production-readiness.md") {
    throw "docs/architecture/README.md does not point to production-readiness.md"
}
if ($index -notmatch "architecture.md") {
    throw "docs/architecture/README.md does not point to architecture.md"
}
if ($index -notmatch "\.agent/") {
    throw "docs/architecture/README.md does not describe the Agent routing boundary"
}

$readiness = Get-Content -LiteralPath "docs\status\production-readiness.md" -Raw -Encoding UTF8
$hasEngineeringClosure = $readiness -match "engineering_closure: completed"
$hasBlockedMeasurement = $readiness -match "measurement: blocked_external"
$hasQualityBoundary = $readiness -match "quality: not_yet_proven"
$hasReadinessBoundary = $readiness -match "production_readiness: not_established"
if (-not $hasEngineeringClosure -or -not $hasBlockedMeasurement -or -not $hasQualityBoundary -or -not $hasReadinessBoundary) {
    throw "production-readiness.md does not describe the final Engineering Closure, measurement, quality and readiness boundaries"
}

Write-Host "Docs verification passed."
