Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $root

$required = @(
    "docs\architecture\README.md",
    "docs\architecture\architecture.md",
    "docs\architecture\production-readiness.md",
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
if ($index -notmatch "\.agent/architecture/architecture.md") {
    throw "docs/architecture/README.md does not describe Agent architecture mirror"
}

$readiness = Get-Content -LiteralPath "docs\architecture\production-readiness.md" -Raw -Encoding UTF8
$hasRuntimeSliceBoundary = $readiness -match "runtime-first vertical slice"
$hasProductionTargetBoundary = $readiness -match "Production Target"
if (-not $hasRuntimeSliceBoundary -or -not $hasProductionTargetBoundary) {
    throw "production-readiness.md does not describe runtime slice and Production Target boundary"
}

Write-Host "Docs verification passed."
