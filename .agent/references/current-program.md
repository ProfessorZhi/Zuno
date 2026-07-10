# Current Program Reference

state: no-active
active_program: none
current_phase: none
latest_completed_program: zuno-evidence-span-agentic-graphrag-hardening-v1

`.agent/programs/` 当前没有 active program。

成熟度和 runtime-first 交付物边界仍以 `docs/architecture/production-readiness.md` 为准。

## 最近完成归档

1. `docs/history/programs/zuno-evidence-span-agentic-graphrag-hardening-v1/`
   - 状态：completed / archived。
   - 完成：evidence-span hardening baseline。
   - 边界：release gate 输出面已完成；fixed EnterpriseRAG measured pass 仍因 local agentic profile run incomplete 而 blocked。
2. `docs/history/programs/zuno-launchable-enterprise-agentic-graphrag-full-closure-v1/`
   - 状态：completed / archived。
   - 完成：Program 3 Mega launchable enterprise Agentic GraphRAG product baseline。
3. `docs/history/programs/zuno-enterprise-document-ingestion-platform-v2/`
   - 状态：completed / archived。
   - 完成：Product V1 local durable ingestion baseline。
4. `docs/history/programs/zuno-production-document-ingestion-and-thread-foundation-v1/`
   - 状态：completed / archived。
5. `docs/history/programs/zuno-production-architecture-and-deliverables-completion-v1/`
   - 状态：completed / archived。
   - 说明：一次性交付型成熟化 program，完成“成熟目标架构和四大总交付物完成”。
6. `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`
   - 状态：completed / archived。
7. `docs/history/programs/zuno-master-architecture-implementation-v1/`
   - 状态：completed / archived。
   - 边界：PHASE01-PHASE12。
8. `docs/history/programs/zuno-eight-deliverables-full-realization-v1/`
   - 状态：completed / archived。
   - 边界：PHASE01-PHASE10。
9. `docs/history/programs/zuno-six-layer-internalization-v1/`
   - 状态：completed / archived。
10. `docs/history/programs/zuno-repo-layout-cleanup-v1/`
   - 状态：completed / archived。

## 历史边界

- Program 3 Mega 的 launchable baseline 结论保持不变：`Launchable enterprise Agentic GraphRAG product baseline completed; production scale external deployments remain replaceable targets.`
- Program 3 Mega 吸收并替代过的 suite / queued 输入仍是历史事实：`zuno-enterprise-agentic-graphrag-production-suite-v1`、`zuno-enterprise-ingestion-async-infrastructure-v1`、`zuno-runtime-subsystems-parallel-v1`、`zuno-agent-planning-integration-v1` 和 `zuno-enterprise-knowledge-eval-benchmark-v1`。
- 历史 Program 3 final alias surface closure 已完成，旧 public import path 只通过 `src/backend/zuno/platform/compatibility/legacy_aliases.py` 注册兼容。
- `zuno-runtime-architecture-upgrade-v1` 和 `zuno-architecture-visuals-v1` 是未来参考 draft，不是 active program。
- evidence-span hardening program 没有把 doc-level recall 写成 strict citation measured pass。
- Basic RAG 和 Static GraphRAG 是评测对照组，不是最终产品模式。
- Codex 多线程工程执行不等于 Zuno 产品 runtime 多 Agent 架构；近期 runtime 主线仍是 Single Controller / Single `GeneralAgent`。

## 当前执行规则

- 每轮开始必须重新确认当前 worktree、branch、`git status --short --branch`、允许范围和禁止范围。
- no-active 状态下不得在 `.agent/programs/` 根目录保留平铺 `PHASE*.md`。
- 新 program 必须从 PHASE01 开始；不得把已归档 phase 文件复制回前台当作 active truth source。
- runtime-first / vertical-slice-first closure guard 保持有效。
- 新 runtime 行为继续遵守 TDD；只写 contract、schema 或 README 不能关闭 runtime phase。
- blocked、prepared、runtime observed 或缺失数据不能写成 measured。
- completed program 必须归档到 `docs/history/programs/`。
