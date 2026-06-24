param(
    [string]$Profile = "dev_offline"
)

$root = Split-Path -Parent $PSScriptRoot
$repo = Split-Path -Parent $root
$evalScript = Join-Path $repo 'src\backend\zuno\evals\contract_review_eval\run_contract_eval.py'

Write-Output "Repo: $repo"
Write-Output "Eval script: $evalScript"
Write-Output "Profile: $Profile"
Write-Output "Update this template after contract_review_eval is implemented."
