# Architecture Doc Template

## Status

Current / Target / Future / History

## Purpose

说明本文档回答什么架构问题，以及读者应该用它做什么决策。

## Scope

- In scope:
- Out of scope:

## Design Narrative

先用文字解释：

- 问题与目标；
- 模块职责；
- 近期精简实现；
- 成熟扩展边界；
- typed contract；
- 状态与事实源；
- 失败语义；
- Security / Observability；
- 完成标准。

架构 Markdown 必须以文字为主，不用连续 Mermaid 图代替设计解释。

## Related Code

- 路径：
- owner：
- 依赖方向：

## Related Tests

- 命令：
- 覆盖内容：
- 仍未测量内容：

## Related Diagrams

- View category：
- Overall / Local：
- Mermaid source：`docs/architecture/architecture-views.md`
- HTML output：`docs/architecture/architecture.html`

## Current Behavior

只写代码、测试、trace/eval 或可复现结果已经证明的事实。

## Target Design

写近期目标设计。未实现内容必须明确标注为 Target。

## Lightweight Implementation

说明当前项目可以采用的最小真实实现，以及哪些复杂基础设施只通过 adapter 预留。

## Future Direction

写长期方向。不要让 Future 进入当前验收或成为近期 blocker。

## Failure Semantics

- blocked reason：
- typed error：
- fallback：
- retry/idempotency：
- trace/audit：

## History

列出被替换或归档的旧方案入口。

## Open Questions

- 问题：
- 为什么仍未决定：
- 决策所需证据：

## Validation

- `git diff --check`
- 相关 verifier：
- 相关 tests：
- 浏览器 Mermaid 检查：

## Docs Sync

- `docs/architecture/README.md`
- `docs/architecture/architecture.md`
- `docs/architecture/architecture-views.md`
- `docs/architecture/architecture.html`
- `docs/architecture/production-readiness.md`
- `.agent/architecture/architecture.md`
- `.agent/architecture/architecture.html`
- `.agent/references/architecture-docs-map.md`
- `.agent/references/diagram-inventory.md`
