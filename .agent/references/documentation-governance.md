# Documentation Governance

## When To Use

当任务涉及文档、架构、README、Mermaid、展示页、`.agent` 工作流、history 归档或用户提出“以后都要这样”的规则时，使用本治理工作流。

## Mental Model

```text
执行前：读入口、查归属、定 Current / Target / Future / History
执行中：记录受影响区域，避免只改单一表面
执行后：同步 docs、HTML、diagram、templates、programs、verifier
```

## Current Truth

- `docs/architecture` 是正式架构文档系统。
- `docs/architecture/architecture.md` 是文字总架构文档，负责用自然语言说清当前事实、目标分层、主链路和实施落点。
- `docs/architecture/architecture.html` 是架构 HTML 展示系统。
- `.agent/architecture/architecture.md` 是 Agent 侧总架构维护文档，必须与正式总架构文档保持一致。
- `.agent/references` 是 Agent 工作流文档系统和元工作流自我维护系统。
- `.agent/templates` 是模板与执行计划系统的一部分。
- `.agent/programs` 是当前执行状态入口。
- 代码、测试、Trace、Eval、README、docs、HTML、`.agent/references` 必须保持一致。
- `docs/` 应少而精、相对稳定；`.agent/` 承载高频变化的 Agent 操作规则、执行计划、模板和治理索引。

## Target Direction

Zuno 最终不是单一 RAG Demo，而是代码、架构文档、Agent 工作流、展示页面都能持续同步演化的工程化项目。

## Must Preserve

- 不允许只改代码不检查架构文档。
- 不允许只改 `.agent` 不更新正式 docs 中的人类可读结论。
- 不允许只改 `architecture.html` 不更新对应 `docs/architecture` 说明。
- 不允许只改 `docs/architecture/architecture.md` 不更新 `.agent/architecture/architecture.md`，或反过来。
- 不允许把 `.agent` 的高频维护细节重复堆进 `docs/`。
- 不允许把 Target / Future 写成 Current。
- 不允许把一次性对话要求误写成全仓长期规则。

## Before Editing

1. 读 `AGENTS.md`。
2. 读 `.agent/references/project-map.md`。
3. 读 `.agent/references/architecture-docs-map.md`。
4. 读 `.agent/references/architecture-update-policy.md`。
5. 如涉及用户新长期规则，读 `.agent/references/workflow-update-policy.md`。
6. 查 `git status --short --branch` 并保护用户未提交改动。

## Allowed Changes

- 补充或修正文档治理规则。
- 更新受影响 docs、HTML 生成器、图清单、模板和 verifier。
- 在 `.agent/programs/current.md` 或 `implementation-roadmap.md` 记录当前状态。

## Forbidden Changes

- 不要为了文档治理改 runtime 业务代码。
- 不要绕过生成器手工维护 `docs/architecture/architecture.html`。
- 不要把 `.agent/templates` 写成项目知识库。

## Common Failure Patterns

- 用户提出长期规则，Agent 只在最终回复里说“以后注意”。
- 更新了架构图标题，但 `EXPECTED_DIAGRAMS`、diagram inventory 和 tests 没同步。
- 新增 reference 文件但 verifier 仍认为它是漂移。

## Debug Playbooks

- 文档冲突：先分 Current / Target / Future / History，再决定是更新 Current 文档、Target 文档还是归档 History。
- 规则冲突：AGENTS.md 保持短入口，详细规则放 `.agent/references`，必要时更新 verifier。
- 生成物冲突：只改源文件和生成器，再重新生成 HTML。

## Focused Tests

```powershell
git diff --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python tools/agent/render_architecture.py --check
```

## Docs Sync

文档治理变更后检查：

- `AGENTS.md`
- `.agent/system.yaml`
- `.agent/references/README.md`
- `.agent/references/workflow-governance.md`
- `.agent/templates/README.md`
- `docs/architecture/README.md`
- `docs/architecture/architecture.md`
- `.agent/architecture/architecture.md`
- `docs/architecture/architecture.html`

## Lessons Learned

治理的目的不是多写文档，而是让下一次修改能自动知道该同步哪里。
