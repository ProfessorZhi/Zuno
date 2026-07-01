# Program Closure Checklist

program: `zuno-production-architecture-and-deliverables-completion-v1`
state: completed / archived

## Phase 顺序

- [x] PHASE01 production maturity gap audit
- [x] PHASE02 program truth source and execution system
- [x] PHASE03 workflow self maintenance automation
- [x] PHASE04 documentation dedup architecture clarity
- [x] PHASE05 repo ownership and compatibility retirement
- [x] PHASE06 product surface desktop recovery loop
- [x] PHASE07 production parse and index platform
- [x] PHASE08 durable agent runtime persistence
- [x] PHASE09 memory context production governance
- [x] PHASE10 tool sandbox vault network runtime
- [x] PHASE11 production graphrag evidence citation
- [x] PHASE12 security trace eval release closure

## 四大总交付物

- [x] 工作流自洽与自我维护：长期规则能被分类、写回、模板化并进入机器检查。
- [x] 文档系统清晰无冗余：前台文档少而精，architecture / production-readiness / program / history 边界清楚。
- [x] 文件夹和代码 ownership 清晰：六层 owner 清楚，compatibility / vendor / legacy alias 只承担必要临时桥接。
- [x] 架构功能完整实现：八类 runtime-first 交付物均有 Current 证据或明确 Remaining Target。

## 八类 runtime-first 交付物

- [x] 产品闭环。
- [x] 文档解析与索引。
- [x] Agent Runtime。
- [x] Memory 与 Context。
- [x] Tool Control Plane 与 Sandbox。
- [x] Knowledge / GraphRAG / Evidence / Citation。
- [x] Security / Trace / Eval / Release。
- [x] 仓库治理与一致性。

## Program Closure 自维护审查

- [x] `AGENTS.md` 已更新。
- [x] `.agent/system.yaml` 的 docs_sync / verify map 已更新。
- [x] `.agent/references/` 已更新 current-program 和 verification-map。
- [x] `.agent/templates/` 不需要新增或修正执行骨架。
- [x] `.agent/programs/` 已完成归档并回到 no-active 等待态。
- [x] completed program 已归档到 `docs/history/programs/`。
- [x] `docs/architecture/architecture.md` 的 Current / Target / Future / History 仍严格区分。
- [x] `.agent/architecture/architecture.md` 与 `docs/architecture/architecture.md` 完全一致。
- [x] 两个 `architecture.html` 由同一个 Markdown 源生成且通过渲染校验。
- [x] verifier / tests 覆盖 no-active 和 latest completed archive 规则。

## 必须归档的证据

- [x] PHASE01 maturity gap audit。
- [x] 四大总交付物 closure table。
- [x] 八类 runtime-first deliverables closure table。
- [x] owner map 和 import matrix。
- [x] external dependency / blocked evidence matrix。
- [x] trace / eval / release baseline。
- [x] full verification log。
- [x] final `git status --short --branch`。
- [x] final commit hash。
- [x] push status。
