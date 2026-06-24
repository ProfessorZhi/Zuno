Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $root

git grep -n "Domain Pack" -- docs AGENTS.md .agent ":(exclude)docs/architecture/history/**"
