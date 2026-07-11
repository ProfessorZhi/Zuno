# Windows PowerShell Runbook

本文件是 Codex 的强制命令规范。默认兼容 Windows PowerShell 5.1，而不是只兼容 PowerShell 7 或 Bash。

## 进入仓库

```powershell
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$Repo = 'F:\internship-work\resume&resume project\02_projects\Zuno'
Set-Location -LiteralPath $Repo

git status --short --branch
if ($LASTEXITCODE -ne 0) { throw 'git status failed' }
```

路径中含空格和 `&`，必须使用 `-LiteralPath`。

## 选择 Python

```powershell
$VenvPython = Join-Path (Get-Location) '.venv\Scripts\python.exe'
if (Test-Path -LiteralPath $VenvPython) {
    $Python = (Resolve-Path -LiteralPath $VenvPython).Path
} else {
    $Python = 'python'
}

& $Python --version
if ($LASTEXITCODE -ne 0) { throw 'Python is unavailable' }
```

不要假设 `python3`、`uv run` 或 Bash venv 路径存在。

## 设置 PYTHONPATH

```powershell
$BackendPath = (Resolve-Path -LiteralPath 'src\backend').Path
$env:PYTHONPATH = $BackendPath
```

不要写 `export NAME=value` 或 `NAME=value command`。

## 运行测试

```powershell
$PytestArgs = @(
    '-m', 'pytest',
    '-q',
    'tests\agent\runtime\test_runtime_state_contract.py',
    'tests\agent\runtime\test_runtime_legacy_adapters.py',
    'tests\agent\test_planning_control_runtime.py',
    '-p', 'no:cacheprovider'
)
& $Python @PytestArgs
if ($LASTEXITCODE -ne 0) { throw 'pytest failed' }
```

Windows PowerShell 5.1 不支持 Bash 风格 `&&`。每条外部命令后检查 `$LASTEXITCODE`。

## 查找文本

```powershell
Get-ChildItem -LiteralPath 'src\backend\zuno' -Recurse -File |
    Select-String -Pattern 'ModelManager|get_user_model|create_agent'
```

不要使用 `grep -R`。

## 删除临时目录

```powershell
$Target = Join-Path (Get-Location) '.local\phase-output'
if (Test-Path -LiteralPath $Target) {
    Remove-Item -LiteralPath $Target -Recurse -Force
}
```

不要使用 `rm -rf`。

## Worktree

```powershell
$WorktreeRoot = 'F:\internship-work\resume&resume project\02_projects\Zuno-worktrees'
$WorktreePath = Join-Path $WorktreeRoot 'runtime-phase05'
$BranchName = 'codex/zuno-unified-runtime-phase05'

git worktree add -b $BranchName $WorktreePath 'codex/zuno-truth-source-production-readiness-baseline'
if ($LASTEXITCODE -ne 0) { throw 'git worktree add failed' }

Set-Location -LiteralPath $WorktreePath
git status --short --branch
```

## 常见错误对照

| 错误写法 | 正确写法 |
| --- | --- |
| `cmd1 && cmd2` | 分开执行并检查 `$LASTEXITCODE` |
| `export PYTHONPATH=src/backend` | `$env:PYTHONPATH = (Resolve-Path 'src\backend').Path` |
| `source .venv/bin/activate` | 直接执行 `.\.venv\Scripts\python.exe` |
| `rm -rf path` | `Remove-Item -LiteralPath path -Recurse -Force` |
| `grep -R text path` | `Get-ChildItem ... | Select-String` |
| 未引用含空格路径 | `Set-Location -LiteralPath '...'` |
| `pytest ...` | `& $Python -m pytest ...` |
