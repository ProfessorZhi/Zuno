# Zuno Production Architecture and Deliverables Completion V1

program: `zuno-production-architecture-and-deliverables-completion-v1`
state: active
current_phase: `PHASE01_production-maturity-gap-audit`

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

## 一次性交付定义

一次性交付指同一个 active program 覆盖全部剩余成熟化工作，并在 PHASE12 统一 release closure；它不表示一个 commit、一个线程或跳过 phase gate。

## 最终验收

- `docs/architecture/production-readiness.md` 中四大总交付物和八类 runtime-first 交付物均有 Current 证据或明确 Remaining Target。
- `.agent/programs/` 完成后归档到 `docs/history/programs/zuno-production-architecture-and-deliverables-completion-v1/`。
- `AGENTS.md`、`README.md`、`.agent/references/current-program.md`、verifier 和 repo tests 对 program 状态一致。
- 完成全量验证、release evidence、commit 和 push。
