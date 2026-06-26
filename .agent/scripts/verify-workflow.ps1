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
Require-Path ".agent\references\workflow-map.md"
Require-Path ".agent\references\skills-map.md"
Require-Path ".agent\references\local-state-map.md"
Require-Path ".agent\references\current_architecture\README.md"
Require-Path ".agent\programs\current.md"
Require-Path ".agent\workflows\docs-maintenance.md"
Require-Path ".agent\workflows\repo-hygiene.md"
Require-Path ".agent\skills\zuno-docs-maintenance\SKILL.md"
Require-Path ".agent\skills\zuno-repo-hygiene\SKILL.md"
Require-Path ".agent\lessons\README.md"
Require-Path ".agent\templates\requirement-intake.md"
Require-Path ".agent\scripts\verify-docs.ps1"
Require-Path ".agent\scripts\verify_agent_system.py"
Require-Path ".agent\scripts\verify_doc_boundaries.py"
Require-Path ".agent\scripts\verify_repo_hygiene.py"
Require-Path ".agent\scripts\grep-legacy.ps1"
Require-Path ".agent\scripts\grep-domain-pack.ps1"
Require-Path ".agent\programs\zuno-target-architecture-migration-v1\README.md"
Require-Path "docs\architecture\history\programs\official-graphrag-cleanup-v1\README.md"
Require-Path "docs\architecture\history\programs\context-memory-agent-runtime-v1\README.md"
Require-Path "docs\architecture\history\README.md"
Require-Path "apps\web\AGENTS.md"
Require-Path "src\backend\zuno\AGENTS.md"
Require-Path "tools\evals\zuno\AGENTS.md"

$gitignore = Get-Content -LiteralPath ".gitignore" -Raw
if ($gitignore -match "(?m)^\.agent/?$") {
    $failures.Add(".gitignore must not ignore the whole .agent directory")
}
foreach ($ignored in @(".agent/local/*", ".agent/local/notes/", ".agent/local/tmp/", ".agent/local/logs/", ".agent/local/secrets/")) {
    if ($gitignore -notmatch [regex]::Escape($ignored)) {
        $failures.Add(".gitignore missing $ignored")
    }
}

if ($gitignore -match "(?m)^apps/web/AGENTS\.md$") {
    $failures.Add(".gitignore must not ignore apps/web/AGENTS.md")
}

$agentText = Get-Content -LiteralPath "AGENTS.md" -Raw
foreach ($required in @("docs/", "AGENTS.md", ".agent/", "docs/architecture/history/", "Self-Maintenance Rule")) {
    if ($agentText -notmatch [regex]::Escape($required)) {
        $failures.Add("AGENTS.md missing required text: $required")
    }
}

$currentProgram = Get-Content -LiteralPath ".agent\references\current-program.md" -Raw
if ($currentProgram -notmatch "zuno-target-architecture-migration-v1") {
    $failures.Add("current-program.md does not point to zuno-target-architecture-migration-v1")
}

if ($failures.Count -gt 0) {
    $failures | ForEach-Object { Write-Error $_ }
    exit 1
}

python .agent\scripts\verify_agent_system.py
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

python .agent\scripts\verify_doc_boundaries.py
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

python .agent\scripts\verify_repo_hygiene.py
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Write-Host "Workflow verification passed."
