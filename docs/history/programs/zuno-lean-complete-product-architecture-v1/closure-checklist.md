# Program Closure Checklist

state: active
active_program: zuno-lean-complete-product-architecture-v1
current_phase: PHASE04_docs-sync-verification-and-closure
latest_completed_program: zuno-evidence-span-agentic-graphrag-hardening-v1

## 必须关闭的事项

- [x] PHASE01：active program 已打开，旧问题、新定位、六域、四图和边界已记录。
- [x] PHASE02：`docs/architecture/architecture.md` 已收缩为 Lean Complete 近期范围，同时保持详细实施蓝图能力。
- [x] PHASE02：六个运行域已按统一模板展开，包含 owner、contract、配置、状态、失败、trace、测试和验收。
- [x] PHASE02：ownership matrix、配置化契约、核心状态对象、restart recovery 边界、质量验收矩阵已写入。
- [x] PHASE02：README、docs README、architecture README、production readiness 和专题文档不再把旧十图 / 11 层 / Production Scale 写成当前主线。
- [x] PHASE03：renderer、HTML、diagram inventory、verifier 和 tests 全部使用四图契约。
- [x] PHASE03：`docs/architecture/architecture.html` 和 `.agent/architecture/architecture.html` 由同一个 Markdown 源生成。
- [ ] PHASE04：验证命令全部通过。
- [ ] PHASE04：program 已归档到 `docs/history/programs/zuno-lean-complete-product-architecture-v1/`。
- [ ] PHASE04：`.agent/programs/` 回到 no-active。
- [ ] PHASE04：提交并推送当前分支。

## 禁止关闭为成功的事项

- [ ] 不把本轮文档重写写成 runtime 质量提升。
- [ ] 不把 `architecture.md` 改成简单宣传页。
- [ ] 不把 Agentic GraphRAG fixed benchmark 写成 measured pass。
- [ ] 不把 Evidence Text Available、strict citation、answer correctness 写成已通过质量门。
- [ ] 不把 Deep GraphRAG 写成完整 product Agentic Runtime。

## 验证命令

```powershell
python tools/agent/render_architecture.py --write
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
pytest -q tests/repo/test_docs_entrypoints.py -p no:cacheprovider
python .agent/scripts/verify_agent_system.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
git diff --check
```

如果修改 repo guardrail，还要运行：

```powershell
pytest -q tests/repo/test_agent_system.py tests/agent_system/test_agent_guardrails.py -p no:cacheprovider
```
