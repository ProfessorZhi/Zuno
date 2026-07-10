[CmdletBinding()]
param(
    [string]$RepoPath = 'F:\internship-work\resume&resume project\02_projects\Zuno',
    [string[]]$PytestTargets = @(
        'tests\repo\test_docs_entrypoints.py',
        'tests\repo\test_current_program_contract.py',
        'tests\repo\test_agent_system.py',
        'tests\agent_system\test_agent_guardrails.py'
    ),
    [switch]$SkipWorkflow
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
Set-Location -LiteralPath $RepoPath

$VenvPython = Join-Path (Get-Location) '.venv\Scripts\python.exe'
if (Test-Path -LiteralPath $VenvPython) {
    $Python = (Resolve-Path -LiteralPath $VenvPython).Path
} else {
    $Python = 'python'
}
$env:PYTHONPATH = (Resolve-Path -LiteralPath 'src\backend').Path

& $Python '.agent\scripts\verify_agent_system.py'
if ($LASTEXITCODE -ne 0) { throw 'verify_agent_system.py failed' }

& $Python 'tools\scripts\verify_current_program.py'
if ($LASTEXITCODE -ne 0) { throw 'verify_current_program.py failed' }

if (-not $SkipWorkflow) {
    & powershell -NoProfile -ExecutionPolicy Bypass -File '.agent\scripts\verify-workflow.ps1'
    if ($LASTEXITCODE -ne 0) { throw 'verify-workflow.ps1 failed' }
}

$PytestArgs = @('-m', 'pytest', '-q')
$PytestArgs += $PytestTargets
$PytestArgs += @('-p', 'no:cacheprovider')
& $Python @PytestArgs
if ($LASTEXITCODE -ne 0) { throw 'pytest failed' }

git diff --check
if ($LASTEXITCODE -ne 0) { throw 'git diff --check failed' }

git status --short --branch
if ($LASTEXITCODE -ne 0) { throw 'git status failed' }
