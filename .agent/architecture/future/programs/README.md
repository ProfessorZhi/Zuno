# Queued Programs

这里保存后续 program 草案。它们不是当前 active program，不能直接执行。打开某个独立 program 时，必须先迁入 `.agent/programs/`，并从 `PHASE01` 开始。

当前 active program 是 `zuno-architecture-detail-and-execution-plan-v1`，执行入口在 `.agent/programs/`。`zuno-eight-deliverables-full-realization-v1` 已完成并归档；本目录中的五个草案已被该 program 吸收为近期实现参考，但仍可作为未来参考输入，不是 active 执行入口；`zuno-six-layer-internalization-v1` 已完成并归档。

## 当前参考输入顺序

1. [zuno-query-router-and-mode-policy-v1](zuno-query-router-and-mode-policy-v1/implementation-roadmap.md)
2. [zuno-context-builder-and-memory-v1](zuno-context-builder-and-memory-v1/implementation-roadmap.md)
3. [zuno-hooks-evidence-trace-v1](zuno-hooks-evidence-trace-v1/implementation-roadmap.md)
4. [zuno-runtime-architecture-upgrade-v1](zuno-runtime-architecture-upgrade-v1/implementation-roadmap.md)
5. [zuno-architecture-visuals-v1](zuno-architecture-visuals-v1/implementation-roadmap.md)

## 为什么这样排

- 先定产品三模式和内部 `query_method`，否则 runtime 改动没有稳定 contract。
- 再做 Context Builder 与 Memory，因为 Agentic RAG 的每一步都依赖 Context Pack。
- 再做 Hooks / Evidence / Trace，因为增强模式需要预算、权限、fallback 和 citation coverage。
- 最后做 runtime slice，避免把 Target 直接写成 Current。
- Visuals 已有三类 Mermaid 图，后续只做截图验证、README 展示和入口 polish。

## 使用规则

- 每次只打开一个 program。
- 打开时把对应 roadmap 和 phase 文件迁入 `.agent/programs/`，并从 `PHASE01` 开始。
- 被替换的 active program 必须先归档到 `docs/history/programs/`。
- 单个 queued roadmap 或 phase 文件必须写明 `queued draft / not active`，避免被误当成当前执行计划。
