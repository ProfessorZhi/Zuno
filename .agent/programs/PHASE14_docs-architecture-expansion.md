# PHASE14 Docs Architecture Expansion

program: zuno-launchable-enterprise-agentic-graphrag-full-closure-v1
phase: PHASE14_docs-architecture-expansion
status: pending

## 目标

把架构文档从总纲扩展为可执行架构说明，同时保持 `docs/architecture/architecture.md` 少而精，避免重复展开到前台根文档。

## 范围

- 更新 `docs/architecture/architecture.md` 总架构摘要和图源。
- 更新 `docs/architecture/production-readiness.md` Current / Target / Future 边界。
- 更新 `docs/architecture/document-ingestion-foundation.md` async ingestion / worker / outbox / OCR-VLM boundary。
- 按需新增稳定架构文档：agent core runtime、capability and skill layer、agentic retrieval planner、eval observability and cost。
- 同步 `.agent/architecture/architecture.md` 和两个 HTML mirror。
- 更新 README、AGENTS、`.agent/references/current-program.md` 和 verifier docs entrypoints。

## 预期专题文档

为了避免 `architecture.md` 无限膨胀，本 phase 只把总纲写进总架构；稳定专题可以拆到以下文档：

- `docs/architecture/agent-core-runtime.md`：Model Gateway、Memory & Context、Planning & Control、Capability Layer 的 Agent Core 运行契约。
- `docs/architecture/capability-and-skill-layer.md`：SkillCard、CapabilityPolicy、Tool / MCP / Knowledge / Artifact capability 边界。
- `docs/architecture/agentic-retrieval-planner.md`：标准检索 / 深度检索、RetrievalPlan、EvidenceBundle、Reflection、Dynamic Replan。
- `docs/architecture/eval-observability-and-cost.md`：ConversationRunMetrics、StageMetrics、EvalComparisonReport、release gate。
- `docs/architecture/knowledge-space-product-configuration.md`：KnowledgeSpaceConfig、创建 Wizard、Settings tabs、Change Impact Preview、file-level status。
- `docs/architecture/input-layer-and-document-processing.md`：格式矩阵、binary ObjectStore、parser workers、PDF / Office / OCR / VLM、async pipeline、file status lifecycle。

这些文档只有在对应代码、tests、trace 或 E2E evidence 出现后才能把能力写成 Current；在 Program 3 执行前期只能写成 Target contract。

## 目标架构拼接点

本 phase 把已经由代码、tests、trace 和 E2E 证明的事实写回正式文档：

- `architecture.md` 说明总分层和主链路。
- `production-readiness.md` 区分 Current Local Slice、Launchable Prototype Target、Production Scale Target。
- `document-ingestion-foundation.md` 说明输入层、worker、object store、outbox、reconciler 和 OCR / VLM boundary。
- 新增架构文档只承载稳定专题，不承载高频 phase 执行细节。
- README / AGENTS / current-program 只写入口摘要，不重复 closure 证据。

本 phase 保证后续读仓库的人能从文档理解：十五个 phase 如何拼成 Agent Core + Capability + Infrastructure + Eval Envelope。

## 并行开发可行性

本 phase 可以由 Workstream I 起草 supporting docs，但 Coordinator 必须拥有最终 wording，尤其是 Current / Target 边界。

可并行：

- Supporting docs draft 与 verifier update 可并行。
- Architecture renderer sync 与 README/AGENTS 摘要更新可分工。

不可并行：

- 多人同时改 `docs/architecture/architecture.md`。
- 未经 Coordinator review 写 Production Scale Target 为 Current。
- 恢复已退休的 split architecture front path。

## 详细执行卡

- 输入依赖：PHASE03-PHASE13 的实际代码、测试、trace、E2E 和 metrics evidence；现有 architecture governance rules。
- 主要交付物：architecture summary、agent core runtime doc、capability/skill doc、agentic retrieval planner doc、input-layer/document-processing doc、knowledge-space product configuration doc、eval/observability/cost doc、production-readiness boundary update。
- 可并行工作包：子文档草稿可并行；`architecture.md` 总入口、Current/Target wording、HTML render 由 Coordinator 收口。
- Coordinator 锁点：Current 只写已证明事实；Target / Production Scale 不得伪装成 Current；Skill/GraphRAG/多 agent runtime 边界必须统一。
- 下游交接：PHASE15 verifier 和 archive 需要 docs entrypoints、architecture mirror、HTML render、README/AGENTS/current-program 同步。
- PR / commit 建议：`docs(architecture): document launchable agentic graphrag baseline`，与 runtime/test commits 分开。

## 禁止范围

- 不把高频执行细节塞进 `docs/`。
- 不恢复已退休的拆分架构前台路径。
- 不把 Production Scale Target 写成 Current。

## 验收闸门

- architecture markdown mirror 与 docs source 完全一致。
- rendered HTML 与 markdown source 同步。
- README / AGENTS / current-program 与 active mega program 一致。
- docs verifier 和 repo verifier 通过。

## 验证命令

```powershell
git diff --check
python tools/agent/render_architecture.py --write
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
```

## 需要先读取

- `docs/architecture/architecture.md`
- `docs/architecture/production-readiness.md`
- `docs/architecture/document-ingestion-foundation.md`
- `.agent/architecture/architecture.md`
- `README.md`
- `AGENTS.md`
- `.agent/references/current-program.md`

## 需要修改的文件

- `docs/architecture/**`
- `.agent/architecture/**`
- `README.md`
- `AGENTS.md`
- `.agent/references/current-program.md`
- verifier / repo tests for doc entrypoints

## 执行拆解

1. 写 docs update map。
2. 更新 architecture markdown source。
3. 运行 renderer 同步 mirror 和 HTML。
4. 更新 README / AGENTS / current-program 摘要。
5. 更新 verifier and tests。
6. 跑 docs verification。

## 多 agent 分工

- Coordinator owner for architecture.md, README, AGENTS。
- Workstream I drafts supporting docs and verifier updates。
- Other workstreams provide current evidence only after tests pass。

## 需要返回的证据

- docs changed list。
- render check output。
- docs verifier output。
- Current / Target / Future boundary summary。

## 停止条件

- 文档需要写成 Current 但没有代码/test/evidence。
- 新增 docs 会破坏 front path slim contract。
- architecture HTML 无法由 markdown source render。
