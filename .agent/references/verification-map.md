# 验证地图

## 每次修改

```powershell
git diff --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_deep_dive_architecture.py
python tools/scripts/verify_architecture_interview_qa.py
python tools/scripts/verify_markdown_internal_links.py
python tools/scripts/verify_repo_structure.py
python tools/scripts/verify_architecture_interview_program.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
```

当前轻量 Lab 边界由 `python tools/scripts/verify_architecture_interview_program.py` 负责；它不创建 Session、不运行红队或蓝队。正式 Round Archive 只验证元数据和 Owner，不重新运行历史 Protocol。

历史 V2–V4.2 Protocol、Round-006 Operational Pilot 和 Gate Realignment 的验证输出属于 Git
历史与 `docs/history/red-blue/` 的考古材料；当前不重新运行旧验证器，也不把历史结果当成当前
工作流能力证明。

当前架构 Red/Blue 任务先读取 `project-reconstruction-lab/WORKFLOW.md`；只有显式调用时才读取对应 Skill、
`docs/architecture/` 和 Facts；需要考古时再读取 `docs/history/red-blue/` 的指定归档。

历史 Round 统一由 `docs/history/red-blue/` 持有；该历史归档不拥有 Canonical Architecture，正式变更必须回到 `docs/architecture/`、`docs/facts/`、`docs/decisions/`、`docs/governance/` 或 `docs/evidence/` 的正确 Owner。

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
