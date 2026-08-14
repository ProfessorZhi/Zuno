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

需要理解架构演进时，按需读取 `docs/history/red-blue/` 的单轮原始记录；它不拥有当前架构，不重新运行历史 Protocol，也不作为生产证据。

## Runtime

Runtime 变更还需按代码 Owner 运行对应 focused pytest、compile、migration 或 integration 验证；文档验证不能替代 Runtime 验证，也不能据此声称 Full CI。
