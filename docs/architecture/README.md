# Zuno 总体架构文档

`docs/architecture/` 是唯一正式总体架构目录，只能保留四个文件：

```text
README.md
architecture.md
architecture-views.md
architecture.html
```

## Canonical Question

Product、Domain、Logical Capability、Physical Service/Deployment、Data、Security 和 Eval 如何形成一个可恢复、可验证、可被简化或替换的跨层目标闭环？

总体架构先回答“为什么做这个系统”，再说明五层责任视图、WorkBuddy / Dify 竞争假设、A/B/C Kill Test 和 State / Failure / Recovery 边界；五层不是最终模块或服务数量。当前文档处于 `READABILITY_BASELINE_REFOUNDED`；下一轮 Red/Blue 前必须通过可读性门。

## 阅读顺序

第一次阅读只读 `architecture.md` 的 Part A：先理解产品问题、Current/Target/History 边界、
责任分层、状态 Owner、失败恢复和替代方案。第二次再读 Part B 的 Contract、State、Retry、
Security 和验证要求。最后按问题进入 `../project/`、`../modules/`、ADR 和 Evidence；不要从术语、服务名
或旧模块编号倒推产品设计。

可读性门的最低问题是：一个不了解 Zuno 的高级工程师，能否不用代码和 Part B 解释“为什么存在、
谁拥有状态、失败如何恢复、什么时候删除”。这不是 Production Readiness 证明，也不冻结服务或
模块数量。

## 文件职责

- `architecture.md`：跨层架构正文、全局边界、状态/失败/恢复语义和 Current/Target/History 解释。
- `architecture-views.md` + `architecture.html`：不可拆分的图源与展示配对，不拥有第二套架构事实。
- `README.md`：目录边界、阅读入口和维护规则，不承载专题 Contract。

## 重要边界

- 本目录不记录项目故事；这些内容统一在 `../project/`。
- 本目录不记录当前运行证据；可复现证据在 `../evidence/`。
- 本目录不记录实施计划、运维 Runbook 或 ADR；这些分别进入 `.agent/programs/`、`docs/operations/` 和 `docs/decisions/`。
- 旧专题和 11 模块不再作为平行 Canonical；Red/Blue 过程归档见 [`../history/red-blue/README.md`](../history/red-blue/README.md)，旧材料由 Git 历史保留。

## 维护

跨层含义变化时修改 `architecture.md`；图形关系变化时同步 `architecture-views.md` 与 `architecture.html`，然后运行：

```powershell
python tools/agent/render_architecture.py --check
python tools/scripts/verify_architecture_document_set.py
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_markdown_internal_links.py
```

不得创建第五个文件、`.agent/architecture/` 镜像或第二套 Domain/Runtime/Service/State registry。
