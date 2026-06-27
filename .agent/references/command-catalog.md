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

## 标准架构检查

```powershell
git grep -n "Native BM25"
git grep -n "RRF"
git grep -n "Summary Compression"
git grep -n "Structured Extraction"
git grep -n "ToolCard"
git grep -n "auto router"
```
