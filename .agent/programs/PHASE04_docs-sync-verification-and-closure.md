# PHASE04 docs-sync-verification-and-closure

status: pending
program: zuno-lean-complete-product-architecture-v1

## 目标

完成文档同步、验证、归档、提交和推送。

## 必跑验证

```powershell
python tools/agent/render_architecture.py --write
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
pytest -q tests/repo/test_docs_entrypoints.py -p no:cacheprovider
python .agent/scripts/verify_agent_system.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
git diff --check
```

如果修改 repo guardrail：

```powershell
pytest -q tests/repo/test_agent_system.py tests/agent_system/test_agent_guardrails.py -p no:cacheprovider
```

## HTML 人工检查

- 恰好四张图。
- 不出现文字溢出。
- 全屏按钮有效。
- Mermaid 能渲染。
- 图适合截图和项目介绍。
- 不再以前台标题突出 4+1 或 View & Beyond。
- Markdown 与 HTML 的项目定位一致。

## 归档

完成后归档到：

```text
docs/history/programs/zuno-lean-complete-product-architecture-v1/
```

并将 `.agent/programs/` 恢复为 no-active。

## 最终声明

本轮只收缩和重写目标架构，没有声称运行质量已经提升。Agentic GraphRAG 是否真正完成，仍以 fixed benchmark 和 release gate 为准。
