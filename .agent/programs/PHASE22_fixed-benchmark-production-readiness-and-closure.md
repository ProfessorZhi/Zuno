# PHASE22 Fixed Benchmark, Clean Target Tree and Program Closure

phase_id: PHASE22
status: planned
depends_on: PHASE21
owner: Coordinator / Release Governance

## Phase 目标

运行固定、可比较的 EnterpriseRAG Benchmark，执行 Release Gate；结束 Rollback Window；删除所有旧架构代码、Legacy 目录/文件、alias registry、永久 Feature Flag、双写和旧前端；整理为清晰 Canonical Target 目录；完成最终验证、Production Readiness 评估、状态同步和 Program 归档。

## Minimal Read Set

- PHASE01 Requirement/Legacy/Frontend Inventory
- PHASE02 Compatibility/Cutover Matrix
- PHASE20 Eval/Gate
- PHASE21 Full Validation/Removal Candidates
- 十一模块完成证据
- `docs/status/production-readiness.md`

## Current Anchors

```text
tracked fixed benchmark datasets
release gate configuration
feature flag registry
platform/compatibility/legacy_aliases.py
tests/legacy_guards/**
all production roots containing legacy/compatibility aliases
old API/services/stores/routes/import paths
program files and evidence
```

## Allowed Paths

```text
all paths explicitly listed in PHASE21 removal candidates
tools/evals/zuno/**
tools/scripts/*structure*|*boundary*|*program*.py
tests/repo/**
docs/status/**
docs/evidence/**
.agent/references/**
.agent/programs/** for closure/archive
```

## Forbidden Paths

- 为删除旧代码改变新架构 Contract/Owner。
- 在 Benchmark 失败时降低阈值或删除关键 Slice。
- 因“可能有人用”保留无 Owner、无期限的 Legacy 文件夹。
- 未运行验证就写 Production Ready。

## Work Packages

### P22-T01 Fixed Dataset and Profile Execution
- Goal：跟踪固定 Case Set/Hash，运行 standard/local/deep/agentic 同 Dataset、Corpus、Snapshot、Model/Judge/Embedding/Metric/Security 配置。
- Tests：profile completeness、reproducibility、case hash、environment manifest、rerun variance。
- Acceptance：依赖不可用如实 BLOCKED；不得以 sample/mock 替代正式 measured。

### P22-T02 Benchmark Comparison and Release Decision
- Goal：生成 Core Five、Citation/Safety、Critical Slice、Agent Efficiency、Cost/Latency、Failure Bucket 和 Gate。
- Acceptance：输出 PASSED/FAILED/BLOCKED/INCOMPARABLE/ERROR；只有 Comparable+Measured 才声明质量结论。
- Evidence：immutable results/artifact hash/config/reproduce command。

### P22-T03 Legacy-free Canonical Directory Cleanup
- Goal：根据 removal candidates 删除旧 Runtime、旧 API/Store、旧 Tool/Model/RAG/Memory paths、临时 compatibility bridge、Feature Flag 分支和旧前端。
- Mandatory deletion：
  - `src/backend/zuno/platform/compatibility/legacy_aliases.py`；
  - 仅为 alias 存在的 `platform/compatibility/` 目录；
  - `tests/legacy_guards/**`，改为 canonical boundary tests；
  - 生产源码下名称为 `legacy`、`legacy_*`、`*_legacy` 的目录/文件；
  - 已过 Rollback Window 的 GeneralAgent/旧 Runtime 主路径、旧 DTO/Store/Route；
  - 临时 dual-read/dual-write 和 migration flags。
- External compatibility：确需支持的公开 API 版本放在清晰 `api/product/v1|v2` Adapter，不得放 Legacy 目录，不得拥有领域事实。
- Tests：全仓 import/reference search、package import、frontend bundle、migration data verification、boundary verifier。
- Acceptance：生产源码树零 Legacy 文件夹、零 alias registry、零永久旧架构；目录只反映 Canonical Owner。

### P22-T04 Canonical Structure and Dependency Enforcement
- Goal：更新 code map、ownership matrix、package README、static dependency guard，保证六个物理根内目录清晰。
- Tests：禁止旧 root imports、跨 Owner DB writes、Provider/Tool bypass、API→Domain reverse dependency、frontend internal enum import。
- Acceptance：新代码无法重新引入 Legacy 目录或双 Owner。

### P22-T05 Full Final Verification
- Goal：在清理后的最终树运行完整 repo、backend、frontend、desktop、Migration、Postgres/RabbitMQ/Object/Checkpointer、Fault、Security、E2E、Load/Soak、Backup/Restore。
- Evidence：命令、版本、环境、结果、失败和未运行项。
- Acceptance：任何因删除旧路径暴露的失败必须修新路径，不能恢复 Legacy 文件夹。

### P22-T06 Production Readiness and Status Truth
- Goal：逐项评估 design/implementation/runtime observed/measured/quality proven/production ready，更新 `production-readiness.md`、Requirement Ledger 和 Evidence Registry。
- Tests：状态文档 verifier；每个 Current/Measured/Ready 声明有 evidence ref。
- Acceptance：完整实现不自动等于 Production Ready；缺安全/DR/load/ops 证据则保持未建立。

### P22-T07 Program Archive and No-active Reset
- Goal：生成 closure summary、commit map、migration map、verification report、known limitations；整体归档 Program。
- Steps：复制 active Program 和 work products 到 `docs/history/programs/zuno-canonical-architecture-runtime-realization-v1/`；更新 `.agent/references/current-program.md`；`.agent/programs/` 恢复 no-active。
- Tests：current program verifier、history links、no duplicate active truth、clean git tree。
- Acceptance：归档后不存在竞争 Program；Canonical Runtime 和清晰目录是唯一 Current 主线。

## Phase 完成定义

- 固定 Benchmark 有真实状态和 Evidence。
- 新架构是唯一主路径。
- 生产源码、Web、Desktop 零 Legacy 文件夹/文件/alias registry/永久双路径。
- 完整验证和状态更新诚实完成。
- Program 归档，前台 no-active。

## Validation

```bash
git diff --check
python tools/scripts/verify_current_program.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python tools/scripts/verify_architecture_document_set.py
python tools/scripts/verify_architecture_semantic_alignment.py
python tools/scripts/verify_wave1_contract_freeze.py
pytest -q -p no:cacheprovider
cd apps/web && npm run lint && npm run build
# browser E2E, desktop build/smoke, migrations, infra fault/load/DR, fixed benchmark commands from evidence manifest
```
