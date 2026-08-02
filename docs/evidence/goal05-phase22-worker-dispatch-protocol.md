# PHASE22 Worker Dispatch Protocol Evidence

status: current_control_plane
parent_pr: 97
phase: PHASE22
production_readiness: not_established

## 目标

本证据记录 PHASE22 后续 Claude Worker 的唯一启动入口。Dispatcher 只负责校验、启动、采集和输出调度结果，不修改业务代码，不提交，不推送，不创建 PR，也不改变 Program 终态。

## 默认入口

默认入口是：

```powershell
.agent/scripts/dispatch_claude_worker.ps1
```

必填参数：

- `-TaskCard`
- `-Worktree`
- `-Provider MiniMax|DeepSeek`
- `-ParentPR`
- `-Repository`
- `-WorkPackage`
- `-ExpectedBranch`
- `-MaxTurns`

可选参数：

- `-ResumeSessionId`
- `-OutputDirectory`

实际 metrics runner 默认指向：

```text
F:\funny_project\agent-metrics-workspace\agent-metrics-collector\scripts\run-claude-with-metrics.ps1
```

## 强制闸门

Task Card 闸门要求读取完整 UTF-8 正文，长度不少于 800 字符，并包含 `WORKER_TASK_ID`、`Allowed Paths`、`Forbidden Paths` 或 `no-governance-write`、`Required Checks`、`Completion Contract`、`COMMIT_SHA`、`TEST_RESULTS`、`BLOCKERS` 和 `BLOCKED_PROMPT_TRUNCATED`。Dispatcher 只记录 prompt 的 SHA-256、长度和 task id，不记录正文。

Worktree 闸门要求目标是 Git 仓库，当前分支等于 `ExpectedBranch`，分支不得为 `main`，工作区必须 clean，`HEAD`、`Repository` 和 `ParentPR` 可解析，并通过 worktree lock 防止同一 worktree 被并发 worker 共享。

Provider 闸门把执行能力和额度快照分开。MiniMax 的 `quota_snapshot_available=CONFIG_REQUIRED` 不阻塞 `execution_available=AVAILABLE`。Token 和成本只能来自 metrics summary，Codex App 主线程 token 状态记录为 `NOT_AVAILABLE_APP_SESSION`。

## Prompt 注入

Dispatcher 使用完整 Task Card 正文注入 Claude：

```powershell
$Prompt = Get-Content -LiteralPath $TaskCard -Raw
$ClaudeArgsJson = ConvertTo-Json @(
  "-p",
  $Prompt,
  "--output-format",
  "stream-json",
  "--verbose",
  "--max-turns",
  "$MaxTurns"
) -Compress
```

禁止把 Task Card 路径、标题或第一行当作 prompt。

## 输出

每个 segment 生成独立目录，至少包含：

- `dispatch-result.json`
- `worker-stdout.log`
- `worker-stderr.log`

日志和结果必须脱敏，不得泄露 prompt 正文、Task Card 路径、完整 Home Path、Email、密钥或 token。

## Worker 完成判定

Worker 最终结果必须符合 `.agent/programs/worker-result.schema.json`。Dispatcher 只接受三类可审查结果：

- `COMMIT_SHA`、`CHANGED_FILES`、`TEST_COMMANDS`、`TEST_RESULTS` 且 worktree clean。
- `PATCH` 或 `EVIDENCE`，同时给出精确 `BLOCKERS`，且 worktree clean。
- `BLOCKED_<REASON>`，同时给出精确 `BLOCKERS`，且 worktree clean。

仅有分析、建议、未提交修改或无 blocker 的输出，必须标记为 `FAILED_WORKER_COMPLETION` 或 `REVIEWED_PARTIAL`，不得写成 `COMPLETED`。

## 当前边界

该协议只解除 worker 调度控制面的阻塞，不关闭 PHASE22，不设置 production ready，不批准 reviewer，不设置 benchmark eligibility，不归档 Program。
