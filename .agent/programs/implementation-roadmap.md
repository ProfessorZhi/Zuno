# Zuno Production Architecture and Deliverables Completion V1

program: `zuno-production-architecture-and-deliverables-completion-v1`
state: active
current_phase: `PHASE05_repo-ownership-and-compatibility-retirement`

## 核心目标

把 Zuno 从第一版 runtime-first vertical slice 推进到成熟目标架构和四大总交付物完成。四大总交付物是：

1. 工作流自洽与自我维护。
2. 文档系统清晰无冗余。
3. 文件夹和代码 ownership 清晰。
4. 架构功能完整实现；该项展开为八类 runtime-first 交付物。

## 非目标

- 不把 Target / Future 写成 Current。
- 不把 Codex 多 agent 执行方式改写成 Zuno 产品 runtime 多 Agent 架构。
- 不直接删除 compatibility、vendor、legacy alias 或旧 provider path；必须先有 owner map、import matrix、替代路径和 tests。
- 不引入 Java、微服务或事件驱动 worker 作为近期默认实现，除非用户单独打开 Future 方向。

## Phase 路线

| Phase | 名称 | 目标交付 |
| --- | --- | --- |
| PHASE01 | production maturity gap audit | 对四大总交付物和八类 runtime target 做证据审计、owner map、验证矩阵和停止条件。 |
| PHASE02 | program truth source and execution system | 冻结 active program 真相源、phase gate、thread prompt 规则、verifier 期望和多 worktree 执行计划。 |
| PHASE03 | workflow self maintenance automation | 把长期规则写回、program open/close、docs sync、history archive 和 verifier 更新做成自维护闭环。 |
| PHASE04 | documentation dedup architecture clarity | 压缩前台文档，保证 architecture / production-readiness / program / history 各司其职。 |
| PHASE05 | repo ownership and compatibility retirement | 深度治理六层 ownership、platform/services、compatibility、vendor、provider tree 和 legacy alias。 |
| PHASE06 | product surface desktop recovery loop | 完成 Desktop、下载、长任务恢复、错误恢复、artifact / feedback / trace 产品化。 |
| PHASE07 | production parse and index platform | 完成 parser queue、深度 OCR/layout/table/code 抽取、外部索引 adapter 和 index operations。 |
| PHASE08 | durable agent runtime persistence | 完成 LangGraph-compatible persistence、进程重启恢复、approval wait/resume、cancel 和 exactly-once tool boundary。 |
| PHASE09 | memory context production governance | 完成 semantic/vector memory、后台治理 scheduler、隐私删除平台和 memory eval baseline。 |
| PHASE10 | tool sandbox vault network runtime | 完成真实隔离 sandbox、外部 vault/OAuth broker、网络代理、持久 approval DB 和 audit。 |
| PHASE11 | production graphrag evidence citation | 完成 GraphRAG extraction、community report、RRF/rerank、外部图索引、unsupported claim guard 和 evidence eval。 |
| PHASE12 | security trace eval release closure | 完成外部 trace/eval、online eval、CI release gate、生产运维证据归档、全量验证和 program 归档。 |

## PHASE01 审计结果

PHASE01 已完成生产成熟度差距审计。后续执行必须以 `.agent/programs/PHASE01_production-maturity-gap-audit.md` 中的四大总交付物 gap 表、八类 runtime-first gap 表、owner map、external dependency matrix 和 PHASE02-PHASE12 风险排序为 gate。

PHASE01 结论：

- Current 只包括第一版 in-process runtime slice、Web workspace Agent 产品闭环、本地 deterministic parse / index / retrieval / tool / trace / eval surface、focused tests、repo verifiers 和历史 release evidence。
- Production Target 仍包括 production Desktop、parser queue、深度解析、外部索引、production persistence、semantic/vector memory、真实 sandbox、外部 vault、外部 trace/eval 和 CI release gate operations。
- 外部服务、凭据或真实隔离运行时不可用时，后续 phase 只能交付 adapter、local fallback、blocked evidence 和 Remaining Target，不能写成 Current。

## 一次性交付定义

一次性交付指同一个 active program 覆盖全部剩余成熟化工作，并在 PHASE12 统一 release closure；它不表示一个 commit、一个线程或跳过 phase gate。

## 执行分层

本 program 分三层推进：

1. **Truth / Governance 层**：PHASE01-PHASE04。先证明还差什么、谁是事实源、文档如何不双轨、workflow 如何自维护。
2. **Ownership / Runtime Productionization 层**：PHASE05-PHASE11。按 owner 清晰度、产品闭环、parse/index、Agent Runtime、Memory、Tool/Sandbox、GraphRAG/Evidence 推进生产化。
3. **Release Closure 层**：PHASE12。只在证据链完整后更新 Current、归档 program、运行全量验证并推送。

## 全局完成定义

每个 phase 关闭时必须同时满足：

- phase 文件 `status` 从 `active` 或 `pending` 更新为 `completed`，并写明完成证据。
- 修改过的事实源、代码、测试和 verifier 彼此一致。
- 至少运行 phase 文件列出的最小验证命令。
- 如能力不能完成，必须记录 blocked evidence，并保留为 Remaining Target / Future，不得伪装为 Current。
- commit message 必须能看出 phase 和交付物范围。

## 证据类型

允许关闭 phase 的证据包括：

- runtime 代码路径和 focused tests。
- API / UI / Desktop / event stream 的可复现运行证据。
- trace / eval / release baseline。
- verifier / repo tests。
- 外部依赖 blocked evidence 和 local fallback。

不允许单独关闭 phase 的证据：

- 只有 README。
- 只有 schema。
- 只有 contract。
- 只有计划或提示词。
- 只有截图但没有可复现路径。

## 多线程执行规则

- 主线程先盘点可复用 Codex 线程和 worktree，再写 thread prompts。
- 子线程必须使用独立 worktree 和 `codex/` 分支。
- 子线程只处理不重叠写入范围。
- 共享文件由主线程收口：`AGENTS.md`、`README.md`、`.agent/system.yaml`、`.agent/programs/*`、`docs/architecture/*`、core verifier、repo tests。
- 每个子线程完成前必须验证、提交、推送；主线程必须读 diff、检查提交、运行集成验证后再合并。

## Phase 间依赖

- PHASE01 是所有后续工作的差距审计 gate。
- PHASE02 必须在大规模并行前完成，否则 thread prompt 和 verifier 口径会漂移。
- PHASE03-PHASE04 是 workflow / docs 自维护 gate，避免后续生产化改动导致前台双轨。
- PHASE05 是 runtime 物理 ownership gate，PHASE06-PHASE11 不应继续扩大旧 owner。
- PHASE08 durable runtime 是 PHASE06 长任务恢复、PHASE10 exactly-once tool boundary 和 PHASE12 release replay 的关键依赖。
- PHASE12 不能在 PHASE01-PHASE11 未完成或未记录 blocked evidence 时关闭。

## 最终验收

- `docs/architecture/production-readiness.md` 中四大总交付物和八类 runtime-first 交付物均有 Current 证据或明确 Remaining Target。
- `.agent/programs/` 完成后归档到 `docs/history/programs/zuno-production-architecture-and-deliverables-completion-v1/`。
- `AGENTS.md`、`README.md`、`.agent/references/current-program.md`、verifier 和 repo tests 对 program 状态一致。
- 完成全量验证、release evidence、commit 和 push。
