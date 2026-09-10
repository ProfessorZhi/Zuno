# 验证地图

## 文档修改

```powershell
git diff --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_markdown_internal_links.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
```

## 架构修改

```powershell
python tools/agent/render_architecture.py --check
python tools/scripts/verify_architecture_document_set.py
python tools/scripts/verify_architecture_semantic_alignment.py
python tools/scripts/verify_architecture_writing_standard.py
python tools/scripts/verify_architecture_human_readability.py
```

需要理解架构演进时，优先读取 `docs/red-blue/rounds/` 的新式 Round；更早的手工/自动记录只在 `docs/red-blue/archive/legacy/`。这些 review 记录都不拥有当前架构，不作为生产证据。

## Runtime

Runtime 变更还需按代码 Owner 运行对应 focused pytest、compile、migration 或 integration 验证；文档验证不能替代 Runtime 验证，也不能据此声称 Full CI。

当前仓库没有一个可替代上述 Owner-specific verification 的全项目 Runtime GitHub CI。若需要把 selected-suite 结果升级成 Current Evidence，记录必须绑定同一 commit SHA、测试集合、依赖环境、pass/skip/fail 和 blocked reason。
