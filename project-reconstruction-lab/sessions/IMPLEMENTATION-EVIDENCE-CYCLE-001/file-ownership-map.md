# IMPLEMENTATION-EVIDENCE-CYCLE-001 文件 Ownership Map

基线：`a402683f245e1e4b31c3b2c31b4d352eb9f9a23f`

本轮只有一个执行线程；下表仍然显式记录两个 Task 的写入边界，防止共享文件被无协调地修改。

| Task | Owner 文件/目录 | 允许修改 | 明确禁止 |
|---|---|---|---|
| TASK-001 | `src/backend/zuno/domain/`、`infra/db/alembic/versions/20260813_57_wave001_domain_mutation.py`、`tests/domain/` | Domain Mutation Command、CAS、幂等、持久化、migration、事务/并发/恢复测试 | Agent Planner、Multi-Agent、Tool Runtime、Provider、Event Sourcing、2PC、Saga |
| TASK-003 | `src/backend/zuno/knowledge/provenance.py`、`src/backend/zuno/agent/runtime/synthesis/`、`tests/knowledge/`、相关 citation fixture | Citation identity、lineage guard、Runtime binding 和负例测试 | 新 Document/Evidence 存储模型、LLM Judge、自动换 span、自动换文档 |
| Shared contract | `src/backend/zuno/agent/domain/finalization/`、`tests/agent/runtime/test_runtime_grounded_synthesis.py` | 仅补充最终绑定所需 provenance 字段和严格 fixture | 修改 Domain Owner、重写 Final Gate、改变 Runtime State ownership |
| Review/evidence | `project-reconstruction-lab/sessions/IMPLEMENTATION-EVIDENCE-CYCLE-001/`、`.agent/programs/current.md`、`.agent/references/current-program.md` | 实施证据、交接状态、验证记录 | 把实现证据写成 Production Ready 或关闭原始 P0 |
