# PHASE04 Infrastructure Docs Governance Evidence（历史）

> 当前状态：`SUPERSEDED`。本文件保留 2026-07-18 的镜像治理证据；当前正式治理已移除 `.agent/architecture/` 与 `.agent/modules/`，不能按旧 Verification Results 恢复镜像。

phase_id: PHASE04
task_id: P04-T07
requirement_ids:
  - ARCH-INFRA-001
  - ARCH-INFRA-002
status: implementation_available
date: 2026-07-18

## 边界

本证据证明 Infrastructure 模块的文档治理边界已可机器验证：`Current / Target / Future / Not Selected` 分层存在且被 target protocol 固定；`docs/architecture/` 与 `.agent/architecture/` 只保留四个 canonical 文件；`docs/modules/11-infrastructure.md` 是唯一正式 Infrastructure Target 文档，`.agent/modules/11-infrastructure.md` 是 byte-identical Agent 镜像。

本证据不证明任何 runtime adapter、Checkpointer、Backup/Restore/PITR、RecoverySet 或故障恢复已经完成。它只证明 Target→Current 的文档边界和镜像治理可验证。

## 后续治理说明

上面的镜像结论是 2026-07-18 该证据生成时的历史事实。PHASE22 收口后的正式治理已经移除 `.agent/architecture/` 与 `.agent/modules/`；当前唯一正式架构和模块事实源是 `docs/`，`.agent/` 只保留项目级 Skill、路由、验证器、模板和执行状态。历史 Verification Results 保留，不得据此重新创建镜像目录。

## Verification Results

- current_target_future_not_selected_layering: passed
- single_formal_infrastructure_target_document: passed
- agent_infrastructure_mirror_byte_identical: passed
- formal_architecture_source_only: passed
- architecture_canonical_file_set: passed
- architecture_mirror_byte_identical: passed
- docs_entrypoint_gate: passed
- phase_completion: blocked_official_checkpointer_and_full_recovery_set

## Commands

```powershell
python tools/scripts/verify_phase04_infrastructure_docs_governance.py
```

Expected result:

```text
PHASE04 infrastructure docs governance verification passed.
```

```powershell
pytest -q tests/repo/test_phase04_infrastructure_docs_governance.py -p no:cacheprovider
```

Expected result:

```text
2 passed
```

## Current

- `docs/modules/11-infrastructure.md` 包含 `Current Inventory`、`Target Selection`、`Future Optional`、`Explicitly Not Selected` 和 `Target → Current Evidence`。
- `.agent/modules/11-infrastructure.md` 与正式文档 byte-identical。
- `docs/architecture/` 与 `.agent/architecture/` 均只包含 `README.md`、`architecture.md`、`architecture-views.md`、`architecture.html`。
- `tools/scripts/verify_docs_entrypoints.py`、`tools/scripts/verify_architecture_document_set.py` 和 `tools/scripts/verify_infrastructure_target_protocols.py` 共同保护入口、镜像、模块文档集合和 Infrastructure Target 协议。

## Remaining Target

- 仍未完成的 Infrastructure runtime、Checkpointer、PITR、RecoverySet、Audit runtime 和 cross-tenant hit runtime 不能从本证据推导为 Current。
