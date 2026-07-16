# PHASE01 Requirement Ledger Evidence

task_id: P01-T03
branch: codex/P01-T03-requirement-ledger-traceability
start_commit: 688a50fa5730f8815b2f09050f01eeb42633ae1d
environment: Windows PowerShell, Python local runtime, repository worktree `C:\Users\Administrator\.codex\worktrees\a203\Zuno`

## Current

- 已存在代码：本任务不修改 Runtime 代码。P01-T03 的 Current 只限 `.agent/programs/work-products/requirement-ledger.yaml`、`tools/scripts/verify_phase01_complete_baseline.py` 和 `tests/repo/test_phase01_complete_baseline.py` 对 Requirement Ledger 的可机器验证审计能力。
- 已存在数据：旧 ledger 有 602 项，缺少 Knowledge、Tool、Observability / Eval 三类 Mandatory `ARCH-*`，且缺 reviewer、reverse trace、非空 test/evidence 的完整校验。
- 已存在测试：`tests/repo/test_phase01_complete_baseline.py` 原本只断言 ledger 仍缺字段；本任务将其改为断言 ledger 已具备双向追踪字段，但 PHASE01 closure 仍因其他 WP 和 Coordinator gate 失败。
- 已存在证据：旧 ledger 没有 `docs/evidence/phase01-*.md` 证据包。本文件补充 P01-T03 证据，不代表 PHASE01 关闭。

## Gap

- 旧 verifier 的 Requirement ID 正则只覆盖一段或两段前缀，并要求 ID 单独成格，漏掉 `ARCH-KNOW-*`、`ARCH-TOOL-*`、`ARCH-OBS-*` 和 `ARCH-OBS-RAG-*`。
- 旧 ledger 对 `target_not_current` 项使用空 `test_ids`、空 `evidence_refs` 和缺失 `reverse_trace_refs`，不能从 planned test/evidence 反查到 requirement。
- 现阶段没有把任何 Mandatory Requirement 声明为 Current；全部保持 `target_not_current`，后续 Phase 必须用真实 code/test/runtime evidence 回填。

## Plan

- Expand：重建 `.agent/programs/work-products/requirement-ledger.yaml`，为 756 项 Mandatory `ARCH-*` 增加完整字段。
- Verify：修正 `tools/scripts/verify_phase01_complete_baseline.py` 的源提取与 ledger 字段校验。
- Contract：更新 `tests/repo/test_phase01_complete_baseline.py`，让 P01-T03 失败条件从“字段缺失”收敛为“其他 Work Package / Coordinator gate 未关闭”。
- 回滚方式：回滚本任务四个允许文件即可恢复旧 ledger/verifier/test/evidence 状态；未修改 Runtime、Migration、公开 API 或模块 Target 文档。

## Source Extraction Method

- Source set：`docs/modules/01-product-surface.md` 到 `docs/modules/11-infrastructure.md`，以及 `docs/governance/wave1-cross-module-contract-registry.md`。
- Extraction rule：只接受 Markdown table 中首列以 `ARCH-[A-Z]+(-[A-Z]+)*-\d{3}` 开头的 Mandatory requirement 行；这覆盖 ID 单独成格和 `ARCH-KNOW-001 Ownership` 这类 ID + title 同格格式。
- Count：756 unique requirement IDs。

## Reverse Trace Method

- 每项 requirement 记录 `reverse_trace_refs`。
- `target:<path>:<line>` 指向 Target source。
- `planned_test:<test_id>` 指向后续 Phase 需要落地的测试。
- `planned_evidence:<needs_evidence:...>` 指向后续 Phase 需要落地的证据。
- 因 P01-T03 不实现 Runtime，全部 `current_status` 保持 `target_not_current`；空证据以 `needs_evidence` 或 `target_not_current` 解释。

## Sample Checks

- `ARCH-KNOW-001` 已进入 ledger，来源为 `docs/modules/03-knowledge-agentic-graphrag.md:1915`。
- `ARCH-TOOL-001` 已进入 ledger，来源为 `docs/modules/08-tool-runtime.md:2212`。
- `ARCH-OBS-RAG-020` 已进入 ledger，来源为 `docs/modules/10-observability-eval.md:2042`。
- `ARCH-PRODUCT-001` 保留 Product Surface owner、PHASE09 target phase 和 planned Product work package。
- `ARCH-XMOD-010` 保留 Wave 1 Contract owner、PHASE03 target phase 和 planned contract work package。

## Artifact Hash

- `.agent/programs/work-products/requirement-ledger.yaml`
- sha256: `08600f5ec5bdb856176656e38e6a93829e8d2015904c5c45fbcf3461855cc93a`

## Commands And Results

- `python tools/scripts/verify_phase01_complete_baseline.py`
  - result: failed as expected for PHASE01 closure.
  - P01-T03-specific result: no missing source IDs, no extra IDs, no count mismatch, no empty `test_ids`, no empty `evidence_refs`, no missing `reverse_trace_refs`, no invalid `target_phase`.
  - remaining failures: stale or incomplete P01-T01/T02/T04/T05 inventories, all WP not `completed`, Coordinator approval pending, PHASE02 gate closed, risk register unassigned-P0 proof missing.

## Not-run Checks

- Full CI, E2E, Fault, Migration, Security, Load and DR checks were not run by P01-T03 because this task only updates ledger traceability and its focused verifier/test.
