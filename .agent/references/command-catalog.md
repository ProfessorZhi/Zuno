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

## 多 Agent / Claude Code 调度

Preferred worktree layout:

```powershell
git -C "F:\internship-work\resume project\Zuno" fetch origin main --prune
git -C "F:\internship-work\resume project\Zuno" worktree add -b codex/<task>-<agent>-<model>-<worker> "F:\internship-work\resume project\worktrees\<agent>-<model>-<worker>" origin/main
git -C "F:\internship-work\resume project\worktrees\<agent>-<model>-<worker>" status --short --branch
```

Preferred Claude Code metrics capture:

```powershell
$Log = Join-Path $env:TEMP "zuno-claude-<agent>-<model>-<worker>.jsonl"
$PromptPath = Join-Path $env:TEMP "zuno-claude-<agent>-<model>-<worker>.prompt.md"
Set-Content -LiteralPath $PromptPath -Encoding UTF8 -Value @'
agent=<agent>
model=<model>
worker=<worker>
cost_scope=single-agent-pr-handoff
worktree=<absolute worktree path>
branch=codex/<task>-<agent>-<model>-<worker>
allowed_paths=<paths>
forbidden_paths=<paths>
commit_message=<type>(<area>): <task> [agent=<agent> model=<model> worker=<worker>]
pr_title=<task> [agent=<agent> model=<model> worker=<worker>]
handoff_fields=identity,session_id,branch,commit,changed_files,validation,risk,duration,api_cost_usd_estimated,provider_quota_basis,cost_scope
'@
$Lines = & claude-<provider> -p (Get-Content -LiteralPath $PromptPath -Raw) --output-format stream-json --verbose --max-turns <n> --max-budget-usd <amount>
$Lines | Set-Content -LiteralPath $Log -Encoding UTF8
```

Preferred Claude Code session creation:

```powershell
$Lines = & claude-<provider> -p (Get-Content -LiteralPath $PromptPath -Raw) --output-format stream-json --verbose --max-turns <n> --max-budget-usd <amount>
$Lines | Set-Content -LiteralPath $Log -Encoding UTF8
$SessionId = ($Lines | ConvertFrom-Json | Where-Object { $_.type -eq "result" } | Select-Object -Last 1).session_id
$SessionId
```

Preferred Claude Code session resume for the same PR / handoff:

```powershell
$ResumeLog = Join-Path $env:TEMP "zuno-claude-<agent>-<model>-<worker>-resume-<n>.jsonl"
$ResumePromptPath = Join-Path $env:TEMP "zuno-claude-<agent>-<model>-<worker>-resume-<n>.prompt.md"
Set-Content -LiteralPath $ResumePromptPath -Encoding UTF8 -Value @'
Resume the same PR / handoff.
agent=<agent>
model=<model>
worker=<worker>
cost_scope=single-agent-pr-handoff
session_id=<session id returned by the first stream-json result>
worktree=<absolute worktree path>
branch=codex/<task>-<agent>-<model>-<worker>
required_result=<specific rework or validation task>
append_cost_to_existing_pr_ledger=true
'@
$ResumeLines = & claude-<provider> --resume <session_id> -p (Get-Content -LiteralPath $ResumePromptPath -Raw) --output-format stream-json --verbose --max-turns <n> --max-budget-usd <amount>
$ResumeLines | Set-Content -LiteralPath $ResumeLog -Encoding UTF8
```

Metrics fields to extract from the final `type=result` event:

```text
session_id
duration_ms
duration_api_ms
total_cost_usd
usage.input_tokens
usage.cache_read_input_tokens
usage.cache_creation_input_tokens
usage.output_tokens
modelUsage.*.costUSD
```

Provider quota fields are separate:

```text
provider_quota_basis=token | request | percent | credit | unknown
provider_quota_before=<manual or unavailable>
provider_quota_after=<manual or unavailable>
provider_quota_delta=<manual or unavailable>
```

PR handoff must include:

```text
agent=<agent>
model=<model>
worker=<worker>
cost_scope=single-agent-pr-handoff
session_id=<session id>
branch=<branch>
commit=<sha>
api_cost_usd_estimated=<total_cost_usd>
provider_quota_basis=<basis>
duration_ms=<duration_ms>
validation=<commands and results>
coordinator_score=<0-100, filled by coordinator>
coordinator_decision=accept | request_changes | reject | blocked
```

Cost scope rule:

```text
One worker PR / handoff = one cost ledger row.
Multiple resumes for the same worker PR = append rows and summarize that PR.
Multiple workers in one coordinator conversation = separate PR rows plus coordinator total.
Do not use one chat turn as the accounting unit.
```

Dispatch preference:

```text
Claude Code worker: repetitive docs, evidence, download, environment probing, log extraction, low-risk isolated patches.
Codex coordinator: architecture decisions, root-cause analysis, security/recovery/concurrency/idempotency, review, merge, final verification.
```

Coordinator scorecard:

```text
identity and traceability: 10
scope containment and no unrelated churn: 15
requirement fit and correctness: 20
tests and reproducible verification: 15
evidence quality and honesty: 10
security / approval / audit / no bypass: 15
cost and time efficiency: 5
integration risk and merge readiness: 10

>=85 accept after coordinator verification
70-84 request changes or split/reassign
<70 reject/reassign
security bypass, fake evidence, missing identity, stale-main overwrite, or Target-as-Current claim = blocked
```

Avoid:

- 在 prompt 内嵌套会被 PowerShell 二次解析的双引号 commit message。
- 用 `--output-format text` 统计成本；它不会稳定返回 `usage` 和 `total_cost_usd`。
- 让 worker 直接合并自己的 PR。
- 把一轮对话成本当成单个 PR / agent 成本。
- 为了省 token 把高风险架构判断直接丢给低成本 worker。

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
