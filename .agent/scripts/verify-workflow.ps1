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
Require-Path ".agent\references\code-map.md"
Require-Path ".agent\references\task-routing.md"
Require-Path ".agent\references\workflow.md"
Require-Path ".agent\references\verification-map.md"
Require-Path ".agent\system.yaml"
Require-Path ".agent\programs\current.md"
Require-Path ".agent\programs\implementation-roadmap.md"
Require-Path ".agent\programs\closure-checklist.md"
Require-Path ".agent\architecture\future\programs\README.md"
Require-NoPath ".agent\programs\thread-prompts\THREAD_D_resources-compatibility-physical-migration-prompt.md"
Require-NoPath ".agent\programs\thread-prompts\THREAD_E_target-layer-physical-migration-prompt.md"
Require-NoPath ".agent\programs\PHASE01_workflow-doc-audit.md"
Require-NoPath ".agent\programs\PHASE02_agent-bootloader-routing.md"
Require-NoPath ".agent\programs\PHASE03_skill-template-program-system.md"
Require-NoPath ".agent\programs\PHASE04_workflow-verifiers-drift-tests.md"
Require-NoPath ".agent\programs\PHASE05_closure-history-archive.md"
Require-NoPath ".agent\programs\PHASE06_backend-directory-clarity-audit.md"
Require-NoPath ".agent\programs\PHASE07_fastapi-jwt-auth-compat-retirement-plan.md"
Require-NoPath ".agent\programs\PHASE08_backend-physical-cleanup-slices.md"
Require-NoPath ".agent\programs\PHASE09_target-layout-visual-compat-shell-retirement.md"
Require-NoPath ".agent\programs\PHASE01_alias-inventory-and-target-contract.md"
Require-NoPath ".agent\programs\PHASE02_import-smoke-and-compat-registry-design.md"
Require-NoPath ".agent\programs\PHASE03_low-risk-alias-surface-cleanup.md"
Require-NoPath ".agent\programs\PHASE04_medium-risk-alias-surface-cleanup.md"
Require-NoPath ".agent\programs\PHASE05_high-risk-core-services-settings-cleanup.md"
Require-NoPath ".agent\programs\PHASE06_final-root-surface-guard-and-closure.md"
Require-NoPath ".agent\architecture\future\programs\zuno-target-architecture-refresh-v1"
Require-NoPath ".agent\architecture\future\programs\zuno-repo-layout-cleanup-v1"
Require-NoPath ".agent\programs\zuno-target-runtime-v2"
Require-NoPath ".agent\programs\phase-05-memory-engine.md"
Require-NoPath ".agent\programs\phase-06-capability-tool-retrieval.md"
Require-NoPath ".agent\programs\phase-07-graphrag-llm-entity-extraction.md"
Require-NoPath ".agent\programs\phase-08-langgraph-runtime.md"
Require-NoPath ".agent\programs\phase-09-product-trace-eval-closure.md"
Require-NoPath ".agent\workflows"
Require-NoPath ".agent\skills"
Require-Path ".agent\templates\requirement-intake.md"
Require-Path ".agent\scripts\verify-docs.ps1"
Require-Path ".agent\scripts\verify_agent_system.py"
Require-Path ".agent\scripts\verify_doc_boundaries.py"
Require-Path ".agent\scripts\verify_repo_hygiene.py"
Require-Path ".agent\scripts\grep-legacy.ps1"
Require-Path ".agent\scripts\grep-domain-pack.ps1"
Require-Path "docs\history\programs\zuno-target-architecture-migration-v1\README.md"
Require-Path "docs\history\programs\official-graphrag-cleanup-v1\README.md"
Require-Path "docs\history\programs\context-memory-agent-runtime-v1\README.md"
Require-Path "docs\history\programs\zuno-workflow-doc-system-v1\README.md"
Require-Path "docs\history\programs\zuno-target-architecture-refresh-v1\README.md"
Require-Path "docs\history\programs\zuno-repo-layout-cleanup-v1\README.md"
Require-Path "docs\history\programs\zuno-repo-layout-cleanup-v1\implementation-roadmap.md"
Require-Path "docs\history\programs\zuno-repo-layout-cleanup-v1\PHASE01_repo-layout-audit.md"
Require-Path "docs\history\programs\zuno-repo-layout-cleanup-v1\PHASE05_hygiene-verifier-closure.md"
Require-Path "docs\history\programs\zuno-repo-layout-cleanup-v1\PHASE06_backend-directory-clarity-audit.md"
Require-Path "docs\history\programs\zuno-repo-layout-cleanup-v1\PHASE07_fastapi-jwt-auth-compat-retirement-plan.md"
Require-Path "docs\history\programs\zuno-repo-layout-cleanup-v1\PHASE08_backend-physical-cleanup-slices.md"
Require-Path "docs\history\programs\zuno-repo-layout-cleanup-v1\PHASE09_target-layout-visual-compat-shell-retirement.md"
Require-Path "docs\history\programs\zuno-repo-layout-cleanup-v1\PHASE10_alias-inventory-and-target-contract.md"
Require-Path "docs\history\programs\zuno-repo-layout-cleanup-v1\PHASE11_import-smoke-and-compat-registry-design.md"
Require-Path "docs\history\programs\zuno-repo-layout-cleanup-v1\PHASE12_low-risk-alias-surface-cleanup.md"
Require-Path "docs\history\programs\zuno-repo-layout-cleanup-v1\PHASE13_medium-risk-alias-surface-cleanup.md"
Require-Path "docs\history\programs\zuno-repo-layout-cleanup-v1\PHASE14_high-risk-core-services-settings-cleanup.md"
Require-Path "docs\history\programs\zuno-repo-layout-cleanup-v1\PHASE15_final-root-surface-guard-and-closure.md"
Require-Path "docs\history\README.md"
Require-Path "apps\web\AGENTS.md"
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
foreach ($required in @("docs/", "AGENTS.md", ".agent/", "docs/history/", ".agent/references/task-routing.md", ".agent/references/workflow.md")) {
    if ($agentText -notmatch [regex]::Escape($required)) {
        $failures.Add("AGENTS.md missing required text: $required")
    }
}

$currentProgram = Get-Content -LiteralPath ".agent\references\current-program.md" -Raw
if ($currentProgram -notmatch "state: no-active-program") {
    $failures.Add("current-program.md must declare no active program")
}
if ($currentProgram -notmatch "\.agent/programs/") {
    $failures.Add("current-program.md does not point to the flat program directory")
}
if ($currentProgram -notmatch "zuno-repo-layout-cleanup-v1") {
    $failures.Add("current-program.md missing completed repo layout cleanup program id")
}
if ($currentProgram -notmatch "zuno-runtime-architecture-upgrade-v1" -or $currentProgram -notmatch "zuno-architecture-visuals-v1") {
    $failures.Add("current-program.md missing queued Program 4/5 ids")
}
if ($currentProgram -notmatch "final alias surface closure" -or $currentProgram -notmatch "legacy_aliases.py") {
    $failures.Add("current-program.md missing Program 3 final alias closure completion facts")
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
