# 收口清单

关闭未来 `zuno-target-runtime-v2` phase 前使用这份清单。

## 范围

- 确认当前 phase 是 `implementation-roadmap.md` 里的下一个线性 phase；不要从 Phase 05 跳到 Phase 07。
- 确认 phase 有明确进入条件、涉及 owner、退出标准和聚焦验证证据。
- 确认 phase 没有要求 Java 服务、微服务、事件 worker、数据库 schema 变化、依赖升级、完整前端迁移或 eval baseline 更新，除非该 phase 明确授权。
- 确认没有把 Target 行为写成 Current，除非代码和测试已经证明。
- 确认没有恢复 Domain Pack、`DomainQAGraph`、`MultiAgentSupervisorGraph` 或 `AgentRuntime`。

## 必跑检查

```powershell
git status --short
git diff --check
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_repo_hygiene.py
python .agent/scripts/verify_module_boundaries.py
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
```

如果 phase 修改 runtime 或 eval 代码，还要补聚焦 runtime 或 eval 测试。

## 证据

phase 打开期间，证据记录在 active program 中。phase 关闭且被更瘦的程序表面替代后，把详细证据移到：

```text
docs/history/programs/zuno-target-runtime-v2/
```
