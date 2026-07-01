$root = Split-Path -Parent $PSScriptRoot
$repo = Split-Path -Parent $root
$targets = @(
    (Join-Path $repo 'docs\architecture\README.md'),
    (Join-Path $repo 'docs\architecture\architecture.md'),
    (Join-Path $repo 'docs\architecture\production-readiness.md'),
    (Join-Path $repo 'docs\architecture\architecture.html'),
    (Join-Path $repo 'docs\history\programs\zuno-target-architecture-migration-v1\README.md'),
    (Join-Path $repo 'docs\history\programs\official-graphrag-cleanup-v1\README.md')
)

$targets | ForEach-Object {
    if (Test-Path $_) {
        Write-Output $_
    }
}
