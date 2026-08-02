# 命令目录

## 文档验证门

Preferred:

```powershell
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
```

## Agent 工作流验证门

Preferred:

```powershell
powershell -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
```

## 模块边界验证门

Preferred for target runtime V2 backend boundary work:

```powershell
python .agent/scripts/verify_module_boundaries.py
```

## 前端依赖安装

Preferred:

```powershell
npm ci
```

Avoid `npm install` unless dependency metadata intentionally changes.

## Git 操作

Preferred:

```powershell
git status --short
git diff --check
git commit -m "<message>"
git push
```

Avoid force push, force-with-lease, amend, and reset unless explicitly requested.

## 工作树与命令行安全

Preferred:

```powershell
Get-Location
git rev-parse --show-toplevel
git status --short --branch
git -C <path> status --short --branch
```

适用规则：

- 先确认当前 shell 真在目标 worktree 里，再改文件或跑脚本。
- 读写仓库文件优先使用绝对路径和 `-LiteralPath`。
- 结构化输入（prompt、JSON、长参数）优先走文件，不要依赖多层 shell 透传。
- 测试 launcher 时先隔离 `PATH`，避免系统里真实同名命令干扰。

## 标准架构检查

```powershell
git grep -n "Native BM25"
git grep -n "RRF"
git grep -n "Summary Compression"
git grep -n "Structured Extraction"
git grep -n "ToolCard"
git grep -n "auto router"
```
