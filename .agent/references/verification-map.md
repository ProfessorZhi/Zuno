# 验证地图

## 每次修改

```powershell
git diff --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_deep_dive_architecture.py
python tools/scripts/verify_architecture_interview_qa.py
python tools/scripts/verify_markdown_internal_links.py
python tools/scripts/verify_repo_structure.py
python tools/scripts/verify_red_blue_session.py
python tools/scripts/verify_red_blue_gate_realignment_v1.py
python tools/scripts/verify_red_blue_workflow_v4.py --bootstrap project-reconstruction-lab/sessions/RB-WORKFLOW-V4-BOOTSTRAP
python tools/scripts/verify_red_blue_workflow_v42.py --bootstrap project-reconstruction-lab/sessions/RB-WORKFLOW-V4.2-BOOTSTRAP
python tools/scripts/verify_red_blue_round006_closure.py --round project-reconstruction-lab/sessions/RB-WORKFLOW-V4.2-ROUND-006
python tools/scripts/verify_red_blue_workflow_v42.py --profile batch_adversarial --round project-reconstruction-lab/sessions/<batch-round-id>
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
```

红蓝 Campaign Session 的公开记录一致性由 `python tools/scripts/verify_red_blue_session.py` 负责；它只验证已落盘的 YAML/Markdown 记录，不运行红队、蓝队或架构同步 Runtime。

Round-006 以后使用 `verify_red_blue_workflow_v42.py` 验证 Fresh Context、Dual Thread、相同
Snapshot、Part-A Cold-Start、Red-only interview calibration、Deep-Dive Chain、问题冻结、
Blue-only Canonical Writer、外部 ChatGPT Gate 和双轨状态。它不创建 Session、不启动 Round、
不修改 Canonical，也不代签 Verdict。

Round-006 的中止收口还必须通过 `verify_red_blue_round006_closure.py`；该验证器只确认
`WORKFLOW_EXECUTION_BLOCKER` 与 `ARCHITECTURE_SCORE: INVALID` 的语义，不把工作流失败升级为
架构失败，也不产生 Candidate 或 Merge 证据。

`RB-GATE-REALIGNMENT-001` 使用专用 Gate verifier，检查 Closure Class、无环 Gate 依赖、
用户决策包、原始 P0 记录保持 OPEN，以及 Canonical Sync 未应用。

架构红蓝队任务先读取：

```text
project-reconstruction-lab/README.md
project-reconstruction-lab/00-charter/
project-reconstruction-lab/01-facts/
project-reconstruction-lab/02-history/
project-reconstruction-lab/03-current/
project-reconstruction-lab/05-red-blue/
project-reconstruction-lab/07-interview-red-team/
project-reconstruction-lab/08-decisions/
project-reconstruction-lab/09-implementation/
```

该工作区负责项目事实采集和红蓝互动；`docs/verification/interview-qa/` 负责架构攻击题和 Coverage。两者都不拥有 Canonical Architecture，正式变更必须回到 `docs/project/architecture/`、`docs/project/<topic>/`、`docs/decisions/`、`docs/status/` 或 `docs/evidence/` 的正确 Owner。

## 架构与模块

```powershell
python tools/agent/render_architecture.py --check
python tools/scripts/verify_architecture_document_set.py
python tools/scripts/verify_architecture_writing_standard.py
python tools/scripts/verify_architecture_human_readability.py
python tools/scripts/verify_agent_core_target_protocols.py
```

专题变更再运行对应专题 verifier；旧 11 模块 verifier 不得把 Superseded 文档重新升级为 Canonical。验证器只检查架构不变量，不把目标文档存在当作完成证据。

## Product Runtime

```powershell
pytest -q tests/repo/test_product_runtime_surface.py tests/frontend/test_product_runtime_contracts.py -p no:cacheprovider
python -m compileall -q src/backend/zuno
```

扩展验证：

```powershell
pytest -q tests/api/test_product_artifact_service.py tests/api/test_product_runtime_batch.py -p no:cacheprovider
python tools/scripts/verify_product_surface_target_protocols.py
python tools/scripts/verify_product_runtime_batch.py
```

## 失败处理

验证失败先修复当前事实源或代码根因，再同步 test/verifier；不得删除失败断言，
不得把目录存在、Mock、Target 文档或类名当作生产证据。
