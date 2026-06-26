Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Resolve-Path (Join-Path $PSScriptRoot "..\..")
Set-Location $root

$pattern = "agent" + ".md"
git grep -n $pattern -- . ":(exclude)docs/history/**" ":(exclude).agent/scripts/grep-legacy.ps1"
