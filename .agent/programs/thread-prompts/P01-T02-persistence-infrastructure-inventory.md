# P01-T02 Persistence and Infrastructure Inventory Implementer Prompt

task_id: P01-T02
phase_id: PHASE01
start_commit: c01420e915db19a3b0d6f979ca4450c8d5de0c85
branch: codex/P01-T02-persistence-infrastructure-inventory
owner_module: 11 Infrastructure with all domain owners as consumers

## Objective

重新审计 Persistence and Infrastructure Current。更新 `.agent/programs/work-products/current-persistence-inventory.md`，覆盖 SQLite、PostgreSQL、SQLModel、SQLAlchemy、Alembic、Redis、RabbitMQ、MinIO/S3、Elasticsearch、Milvus、Neo4j、Checkpointer、Backup、Restore、Secret、Object Lifecycle、Worker、Queue、Docker Compose、CI 环境。

## Required Contract

每个 Current 声明必须有：

```text
code
test
runtime/integration evidence
environment
known limitation
physical owner
domain owner
transaction boundary
recovery owner
target phase
```

Compose、配置或 Adapter 声明不能单独算 Current。

## Allowed Paths

```text
.agent/programs/work-products/current-persistence-inventory.md
.agent/programs/work-products/phase-readiness.yaml
docs/evidence/phase01-persistence-infrastructure-inventory.md
tests/repo/test_phase01_complete_baseline.py
tools/scripts/verify_phase01_complete_baseline.py
```

## Forbidden Paths

Runtime behavior, migrations, infrastructure source code, dependency files, Target architecture docs, unrelated phase artifacts.

## State And Failure Semantics

Use status values only from the Program boundary: `implementation available`, `partial implementation available`, `measurement blocked`, `quality not yet proven`, `target_not_current`, `blocked`, `needs_evidence`.

Do not write PostgreSQL/RabbitMQ/MinIO/LangGraph Checkpointer as Current unless real integration evidence exists.

## Verification Commands

```powershell
git diff --check
python tools/scripts/verify_current_program.py
python .agent/scripts/verify_agent_system.py
python tools/scripts/verify_phase01_complete_baseline.py
pytest -q tests/repo/test_current_program_contract.py tests/repo/test_phase01_complete_baseline.py -p no:cacheprovider
```

Disclose if the closure verifier still fails because other PHASE01 tasks are incomplete.

## Evidence Requirements

Write `docs/evidence/phase01-persistence-infrastructure-inventory.md` with commit, environment versions, commands, results, sampled code/test/evidence links, artifact hash, and not-run real dependency checks.

## Completion Report

Commit and push. Include normal evidence, missing real dependency evidence, remaining target, and Stop Conditions.
