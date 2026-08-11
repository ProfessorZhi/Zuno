# 验证地图

## 每次修改

```powershell
git diff --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_deep_dive_architecture.py
python tools/scripts/verify_architecture_interview_qa.py
python tools/scripts/verify_markdown_internal_links.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
```

架构红蓝队任务先读取：

```text
project-red-blue/README.md
project-red-blue/00-charter.md
project-red-blue/01-project-facts.md
project-red-blue/02-project-model.md
project-red-blue/03-team-ownership.md
project-red-blue/04-attack-taxonomy.md
project-red-blue/05-interviewer-personas.md
project-red-blue/06-red-team-protocol.md
project-red-blue/07-blue-team-protocol.md
project-red-blue/08-gap-register.md
project-red-blue/09-open-source-review.md
project-red-blue/10-delivery-evolution.md
```

该工作区负责项目事实采集和红蓝互动；`docs/verification/interview-qa/` 负责架构攻击题和 Coverage。两者都不拥有 Canonical Architecture，正式变更必须回到 `docs/project/architecture/`、`docs/project/modules/`、`docs/decisions/`、`docs/status/` 或 `docs/evidence/` 的正确 Owner。

## 架构与模块

```powershell
python tools/agent/render_architecture.py --check
python tools/scripts/verify_architecture_document_set.py
python tools/scripts/verify_architecture_writing_standard.py
python tools/scripts/verify_architecture_human_readability.py
python tools/scripts/verify_agent_core_target_protocols.py
```

模块变更再运行对应 `verify_<module>_target_protocols.py`。验证器只检查当前
架构不变量，不再检查旧施工计划的完成状态。

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
