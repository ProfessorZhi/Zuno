# Codex Task Backlog

只有 Architecture Accepted 后才能把条目转成真实 Program。User Gate 前允许保留可审计的
Candidate，但不能激活或宣称已实现：

| Task | Preconditions | Forbidden |
|---|---|---|
| 建立 Legal Domain schema | Domain Kernel survives | 不修改生产业务路径 |
| Domain/Runtime reconciliation spike | state boundary accepted | 不把 checkpoint 当 Domain Fact |
| Conditional Retrieval benchmark | Query classes and corpus frozen | 不宣称 GraphRAG 优越 |
| Service boundary spike | scaling/failure/security evidence | 不按 11 modules 拆 11 services |
| OpenViking provider conformance | historical artifact/contract available | 不把历史接入写成 Current Adopt |

当前 Gate Realignment 的第一批候选见
`sessions/RB-GATE-REALIGNMENT-001/implementation-track.md`；它们都不是 active Program。

任务生成模板必须包含 Goal、Scope、Contract、State、Failure、Retry、Recovery、Security、Observability、Migration、Tests、Acceptance Criteria 和 Commands。
