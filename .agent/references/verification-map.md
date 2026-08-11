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
