# Codex Task Backlog

只有 Architecture Accepted 后才能把条目转成真实 Program。当前仅保留候选：

| Task | Preconditions | Forbidden |
|---|---|---|
| 建立 Legal Domain schema | Domain Kernel survives | 不修改生产业务路径 |
| Domain/Runtime reconciliation spike | state boundary accepted | 不把 checkpoint 当 Domain Fact |
| Conditional Retrieval benchmark | Query classes and corpus frozen | 不宣称 GraphRAG 优越 |
| Service boundary spike | scaling/failure/security evidence | 不按 11 modules 拆 11 services |
| OpenViking provider conformance | historical artifact/contract available | 不把历史接入写成 Current Adopt |

任务生成模板必须包含 Goal、Scope、Contract、State、Failure、Retry、Recovery、Security、Observability、Migration、Tests、Acceptance Criteria 和 Commands。
