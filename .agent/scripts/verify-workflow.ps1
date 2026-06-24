Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $root

$failures = New-Object System.Collections.Generic.List[string]

function Require-Path($Path) {
    if (-not (Test-Path -LiteralPath $Path)) {
        $failures.Add("Missing path: $Path")
    }
}

function Require-NoPath($Path) {
    if (Test-Path -LiteralPath $Path) {
        $failures.Add("Unexpected path: $Path")
    }
}

Require-Path "AGENTS.md"
$legacyAgentEntrypoint = "agent" + ".md"
Require-NoPath $legacyAgentEntrypoint
Require-Path ".agent\README.md"
Require-Path ".agent\references\README.md"
Require-Path ".agent\references\current-program.md"
Require-Path ".agent\references\docs-map.md"
Require-Path ".agent\references\code-surfaces.md"
Require-Path ".agent\references\verification-map.md"
Require-Path ".agent\references\current_architecture\README.md"
Require-Path ".agent\templates\requirement-intake.md"
Require-Path ".agent\scripts\verify-docs.ps1"
Require-Path ".agent\scripts\grep-legacy.ps1"
Require-Path ".agent\scripts\grep-domain-pack.ps1"
Require-Path "docs\architecture\programs\official-graphrag-cleanup-v1\README.md"
Require-Path "docs\architecture\history\README.md"

$gitignore = Get-Content -LiteralPath ".gitignore" -Raw
if ($gitignore -match "(?m)^\.agent/?$") {
    $failures.Add(".gitignore must not ignore the whole .agent directory")
}
foreach ($ignored in @(".agent/notes/", ".agent/tmp/", ".agent/logs/", ".agent/local/", ".agent/secrets/")) {
    if ($gitignore -notmatch [regex]::Escape($ignored)) {
        $failures.Add(".gitignore missing $ignored")
    }
}

$agentText = Get-Content -LiteralPath "AGENTS.md" -Raw
foreach ($required in @("docs/", "AGENTS.md", ".agent/", "docs/architecture/history/", "Self-Maintenance Rule")) {
    if ($agentText -notmatch [regex]::Escape($required)) {
        $failures.Add("AGENTS.md missing required text: $required")
    }
}

$currentProgram = Get-Content -LiteralPath ".agent\references\current-program.md" -Raw
if ($currentProgram -notmatch "official-graphrag-cleanup-v1") {
    $failures.Add("current-program.md does not point to official-graphrag-cleanup-v1")
}

if ($failures.Count -gt 0) {
    $failures | ForEach-Object { Write-Error $_ }
    exit 1
}

Write-Host "Workflow verification passed."
