$root = Split-Path -Parent $PSScriptRoot
$repo = Split-Path -Parent $root
$targets = @(
    (Join-Path $repo 'docs\architecture\README.md'),
    (Join-Path $repo 'docs\architecture\zuno_refactor_plan.md'),
    (Join-Path $repo 'docs\architecture\specs\domain-pack-langgraph-graphrag-architecture.md'),
    (Join-Path $repo 'docs\architecture\plans\zuno-refactor-execution-plan.md')
)

$targets | ForEach-Object {
    if (Test-Path $_) {
        Write-Output $_
    }
}
