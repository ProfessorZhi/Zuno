param(
    [string]$Profile = "dev_offline"
)

$root = Split-Path -Parent $PSScriptRoot
$repo = Split-Path -Parent $root
$evalScript = Join-Path $repo 'tools\evals\zuno\contract_review_eval\run_contract_eval.py'

Write-Output "Repo: $repo"
Write-Output "Eval script: $evalScript"
Write-Output "Profile: $Profile"
& python $evalScript --profile $Profile
