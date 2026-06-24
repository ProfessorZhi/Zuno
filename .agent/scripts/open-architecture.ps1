$root = Split-Path -Parent $PSScriptRoot
$repo = Split-Path -Parent $root
$targets = @(
    (Join-Path $repo 'docs\architecture\README.md'),
    (Join-Path $repo 'docs\architecture\current-architecture.md'),
    (Join-Path $repo 'docs\architecture\target-architecture.md'),
    (Join-Path $repo 'docs\architecture\programs\official-graphrag-cleanup-v1\README.md')
)

$targets | ForEach-Object {
    if (Test-Path $_) {
        Write-Output $_
    }
}
