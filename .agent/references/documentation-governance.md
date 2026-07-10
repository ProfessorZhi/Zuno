# Documentation Governance

## When To Use

当任务涉及文档、架构、README、Mermaid、展示页、`.agent` 工作流、history 归档或用户提出“以后都要这样”的规则时，使用本治理工作流。

## Current Truth

- `docs/architecture/architecture.md` 是 Zuno Lean Complete Agentic GraphRAG Product 的详细实施蓝图事实源。
- `docs/architecture/architecture.html` 是从十张 canonical Mermaid 图生成的架构图谱。
- `.agent/architecture/architecture.md` 和 `.agent/architecture/architecture.html` 是生成镜像，不承载独立结论。
- `docs/architecture/production-readiness.md` 只维护 Current、Short-term Closure Gap、Measurement Blocked、Completed 和 Future Optional。
- 专题文档保留运行域技术细节，但服从六个运行域。
- 历史 program 和旧架构材料保留在 `docs/history/`。

## Governance Rules

- 收缩目标范围不等于降低文档精度。
- `architecture.md` 必须能指导 owner、contract、配置、状态、失败、fallback、trace、metrics、tests、Program 和 Phase。
- HTML 不需要复制全部技术细节。
- Current / Target / Future Optional / History 必须分开。
- blocked、prepared、runtime observed 和 measured 必须分开。
- 不把 Agentic GraphRAG implementation available 写成 quality completed。

## Before Editing

1. 读 `AGENTS.md`。
2. 读 `docs/architecture/architecture.md`。
3. 读 `docs/architecture/production-readiness.md`。
4. 读 `.agent/references/docs-map.md` 和 `.agent/references/diagram-inventory.md`。
5. 查 `git status --short --branch` 并保护用户未提交改动。

## Forbidden Changes

- 不为了文档治理改 runtime 业务代码。
- 不手写 `architecture.html`。
- 不恢复 retired split architecture docs。
- 不把 Future Optional 写成短期 blocker。
- 不关闭 verifier 逃避同步。

## Focused Tests

```powershell
git diff --check
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
python .agent/scripts/verify_agent_system.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
```

## Lessons Learned

治理的目的不是多写文档，而是让下一次修改能自动知道哪个 surface 是事实源、哪个 surface 是展示摘要、哪个 surface 是历史证据。
