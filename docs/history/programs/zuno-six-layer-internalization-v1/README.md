# zuno-six-layer-internalization-v1

> 状态：completed / archived。此目录是历史证据，不是当前 active program。

## 目标

在 Program 3 已完成 `src/backend/zuno` root / alias surface closure 后，让 `api / agent / memory / capability / knowledge / platform` 六层内部拥有第一批可解释、可测试、无副作用的目标层薄入口。

## 完成范围

- `memory/` 从纯 facade 推进为 contracts / store / policy / review / retrieval / rendering / engine 薄入口。
- `capability/` 拥有 contracts / registry / selector / policy / execution / trace 薄入口。
- `knowledge/` 拥有 query_service / contracts / evidence / citation / trace / retrieval / fusion / graphrag 薄入口。
- `agent/` 拥有 runtime / context / post_turn / state / streaming / tool_bridge 薄入口。
- `platform/` 拥有 model_gateway / security / observability / storage 薄入口。
- 六层 README 均保留 Current / Target / 禁止事项 / Focused tests 边界。
- repo verifier、Agent verifier、doc boundary verifier 和 repo tests 固定完成态。

归档 phase 范围：PHASE01-07。

## 关键边界

本 program 不改 API response shape、DB schema、frontend、eval baseline、`GeneralAgent` 主循环或旧 public import path。

Capability tools 不按 CLI / API 拆成两棵顶层目录；CLI / API 只是 execution adapter 或 runtime metadata，不是 capability 的主分类。

## 完成验证

最终验证以关闭提交中的命令结果为准：

```powershell
pytest -q
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_repo_hygiene.py
python tools/scripts/verify_docs_entrypoints.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
git diff --check
```

## 后续

后续 queued draft 仍是：

- `.agent/architecture/future/programs/zuno-runtime-architecture-upgrade-v1/`
- `.agent/architecture/future/programs/zuno-architecture-visuals-v1/`
