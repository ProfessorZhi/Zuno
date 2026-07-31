# Agent Contribution & PR Attribution Standard

## 适用范围与目标

本规范定义 Zuno 仓库中所有 AI Agent（包括 Antigravity, Qoder, Codex, Trae, 以及 ChatGPT-Docs 维护者）和 Human 贡献的 Commit Message、PR 标题、Branch 命名与 PR Attribution 描述要求。

## 允许的 Agent 与 Mode

### Agent 识别标识 (Agent)

- `Antigravity`
- `Qoder`
- `Codex`
- `Trae`
- `ChatGPT-Docs`
- `Human`

### Agent 执行模式 (Agent-Mode)

- `Standard-Conversation`
- `Expert-Team`
- `Codex`
- `Standard`
- `Docs-Maintenance`
- `Human`

## Commit Trailer 规范

所有由 Agent 生成或参与的非 Merge Commit，必须在 Commit Message 结尾包含以下 Trailer：

```text
Agent: <AgentName>
Agent-Mode: <AgentMode>
Human-Owner: <HumanUsername>
Architecture-Reviewer: <ReviewerUsername>
Work-Package: <WorkPackageID>
```

示例：

```text
ci: add phase22 remote verification workflow

Agent: Antigravity
Agent-Mode: Standard-Conversation
Human-Owner: ProfessorZhi
Architecture-Reviewer: ChatGPT
Work-Package: AG-PHASE22-REMOTE-VERIFICATION-HARNESS
```

## PR Attribution 规范

每个 PR Body 必须使用 `.github/PULL_REQUEST_TEMPLATE/agent-work-package.md` 模板，并明确包含：

- `## Agent Attribution`
- `## Allowed Scope`
- `## Forbidden Scope`
- `## Current`
- `## Target`
- `## Evidence`
- `## Tests Run`
- `## Tests Not Run`
- `## Not Claimed`
- `## Rollback`

## 验证器

- Commit Trailer 验证: `python tools/scripts/verify_agent_commit_attribution.py --base <sha> --head <sha>`
- PR Body 验证: `python tools/scripts/verify_agent_pr_body.py --file <pr-body.md>`
