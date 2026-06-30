# Zuno Runtime Full 12 Phase Goal Mode Prompt

你现在是 Zuno 主线程目标模式执行者，工作目录：

```text
F:\internship-work\resume&resume project\02_projects\Zuno
```

## 总目标

完整执行当前 active program：

```text
zuno-target-architecture-runtime-full-implementation-v1
```

这不是架构细化、不是 contract foundation、不是“最小可演示实现”。目标是在不推倒既有目标架构的前提下，把 Zuno 推进到完整目标架构第一版 runtime：可运行、可观测、可评测、可交付。

核心闭环必须真实跑通：

```text
上传文档
  -> parse
  -> index
  -> ask
  -> Agentic retrieval
  -> cited answer
  -> trace/eval
  -> artifact/feedback
```

如果一个 phase 只新增 contract、schema、README、diagram、plan、mock 或无副作用 facade，不能关闭该 runtime phase。

## 第一性原则

从用户真实目标出发：用户要的是完整目标架构 runtime 落地，不是又一次最小实现。

每个实现决策都必须回答：

- 它如何推进真实用户闭环？
- 它如何把 Target 变成 Current？
- 它有什么可复现证据：代码、测试、trace、eval、verifier 或 e2e 回放？
- 它是否保持 Zuno 近期产品 runtime 为 Single Controller / Single GeneralAgent？

不要把 Codex 多 agent 工程执行方式误写成 Zuno 产品 runtime 多 Agent 架构。Zuno 近期 runtime 主线仍是 Single Controller Agent。

## 启动门

先运行并汇报：

```powershell
git fetch --prune
git status --short --branch
git log --oneline -5 --decorate
```

然后读取并以仓库当前文件为准，不以旧对话或旧 prompt 为准：

```text
AGENTS.md
.agent/programs/current.md
.agent/programs/implementation-roadmap.md
.agent/programs/closure-checklist.md
.agent/programs/PHASE01_program-reopen-and-truth-source-freeze.md
.agent/programs/PHASE02_runtime-migration-map-and-repo-ownership-lock.md
.agent/programs/PHASE03_task-session-artifact-event-runtime.md
.agent/programs/PHASE04_document-ingestion-parse-runtime.md
.agent/programs/PHASE05_index-jobs-and-knowledge-space-runtime.md
.agent/programs/PHASE06_durable-single-controller-runtime.md
.agent/programs/PHASE07_memory-db-and-context-governance.md
.agent/programs/PHASE08_tool-control-plane-approval-and-sandbox-runtime.md
.agent/programs/PHASE09_agentic-retrieval-evidence-citation-runtime.md
.agent/programs/PHASE10_security-observability-and-online-eval.md
.agent/programs/PHASE11_web-desktop-surface-and-feedback-loop.md
.agent/programs/PHASE12_release-gate-full-e2e-closure.md
docs/architecture/architecture.md
.agent/architecture/architecture.md
.agent/references/current-program.md
.agent/references/code-map.md
.agent/references/runtime-call-chain.md
.agent/references/current-target-future-rules.md
.agent/references/verification-map.md
```

如果 `.agent/programs/current.md` 不是 `zuno-target-architecture-runtime-full-implementation-v1`，不要继续做旧 program。先报告事实漂移，并把 active program 修回 runtime-first program 后再执行。

## 执行模式

默认使用主线程 coordinator + 多 agent / 多 worktree 模式。

主线程职责：

- 确认 worktree、branch、status、允许范围、禁止范围。
- 维护 phase 顺序、依赖关系和 closing criteria。
- 生成或更新子线程提示词到 `.agent/programs/thread-prompts/`。
- 审查每个 worker 的 diff、测试、提交和 push。
- 处理共享文件、冲突、集成验证、最终 merge、归档和 release closure。

多 agent / worker 职责：

- 每个 worker 使用独立 worktree 和独立 `codex/` 分支。
- 每个 worker 只改自己的边界；共享文件由主线程最终收口。
- 每个 worker 完成前必须 focused validation、commit、push。
- worker 总结不能作为验收证据；主线程必须读 diff 和运行验证。

如果当前 Codex UI 不能创建真正目标模式子线程，可以在主线程内使用 subagent 辅助只读审计和互不重叠的实现子任务；但仍由主线程负责最终判断、验证、提交和推送。

## 依赖策略

按 PHASE01 -> PHASE12 关闭状态，不等于所有代码必须完全串行。

必须先完成：

```text
PHASE01 truth source freeze
PHASE02 runtime migration map / ownership lock
```

PHASE02 之后，用 vertical slice 优先推进黄金脊柱：

```text
PHASE03 task/session/event/artifact
  -> PHASE04 parse runtime
  -> PHASE05 index jobs
  -> PHASE06 durable runtime
  -> PHASE09 retrieval/evidence/citation
  -> PHASE10 trace/eval
  -> PHASE11 UI/feedback
  -> PHASE12 release closure
```

PHASE07 memory 和 PHASE08 tool/sandbox 可以与黄金脊柱并行加深，但不能破坏 Single Controller runtime。

## 多 agent workstreams

在 PHASE01/PHASE02 gate 后，按依赖拆出下列 workstreams。不要让两个 worker 同时大改同一批文件。

### A. runtime-ownership

范围：

```text
.agent/references/*
docs/architecture/*
tools/scripts/verify_repo_structure.py
tests/repo/*
src/backend/zuno/**/README.md
```

目标：

- 完成旧 runtime 到六层 target owner 的迁移图。
- 锁定 `platform/services/*`、`zuno.schema/*`、`zuno.database/*`、compat/vendor 的 owner 和冻结规则。
- 增加 verifier/test 防止 Target 被写成 Current。

### B. product-api-event-runtime

范围：

```text
src/backend/zuno/api/**
src/backend/zuno/platform/storage/**
tests/api/**
tests/storage/**
apps/web/src/apis/**
```

目标：

- 实现 workspace、knowledge space、session、file、ingest、task、event、artifact、feedback 的稳定 runtime surface。
- SSE 优先，必须能串起 `workspace_id`、`session_id`、`task_id`、`trace_id`、`artifact_id`、`feedback_id`。
- 不接受只有 TypeScript/Python contract 而没有可跑路径。

### C. ingestion-index-runtime

范围：

```text
src/backend/zuno/knowledge/ingestion/**
src/backend/zuno/knowledge/**
src/backend/zuno/platform/services/convert_files/**
src/backend/zuno/platform/services/pipeline/**
src/backend/zuno/platform/services/rag/**
tests/graphrag/**
tests/retrieval/**
tests/storage/**
```

目标：

- 把 Parse Gateway 从 contract owner 推进到 runtime owner。
- 至少覆盖 PDF、DOCX/PPTX、Markdown/TXT、图片 OCR、代码文件五类主格式；如果某格式依赖外部 binary 不可用，必须有真实 adapter boundary、fixture、skip reason 和可替换实现，不允许假成功。
- 生成 Canonical Document IR、chunk、provenance、ACL、index handoff。
- 建立 BM25 / vector / graph 至少一种真实可查询 index；最终 PHASE05 要为三类索引留下可验证 job/runtime boundary。

### D. durable-agent-memory-runtime

范围：

```text
src/backend/zuno/agent/**
src/backend/zuno/memory/**
src/backend/zuno/platform/storage/**
tests/agent/**
tests/storage/**
```

目标：

- 在既有 harness 节点顺序上实现 durable checkpoint、resume、interrupt、approval wait、cancel、replan。
- 将 memory 从 in-memory foundation 推进到可持久化、可审查、可治理 runtime。
- 保持 Single Controller，不引入默认多 Agent 产品架构。

### E. tool-retrieval-citation-runtime

范围：

```text
src/backend/zuno/capability/**
src/backend/zuno/knowledge/retrieval/**
src/backend/zuno/knowledge/fusion/**
src/backend/zuno/knowledge/graphrag/**
src/backend/zuno/knowledge/agentic_graphrag.py
tests/tools/**
tests/retrieval/**
tests/graphrag/**
```

目标：

- Tool Control Plane 接真实 executor、approval API/UI boundary、credential broker boundary、sandbox profile 和 audit trace。
- Agentic retrieval 消费新的 ingestion/index runtime。
- normal/enhanced/auto 产品模式映射到 basic/local/global/drift 内部方法。
- 输出 EvidenceBundle、CitationBuilder、unsupported claim check 的真实 runtime 证据。

### F. security-eval-observability

范围：

```text
src/backend/zuno/platform/security/**
src/backend/zuno/platform/observability/**
tools/evals/**
tests/evals/**
tests/repo/**
```

目标：

- input、retrieval、tool、output 四道安全闸接真实运行时。
- trace/span、dataset、retrieval eval、answer eval、agent eval、security eval 接入 release baseline。
- 本地持久 trace store 和可选 LangSmith-compatible export adapter 要有可测路径。

### G. web-desktop-release

范围：

```text
apps/web/**
apps/desktop/**
docs/**
.agent/**
README.md
AGENTS.md
tools/agent/**
tools/scripts/**
```

目标：

- 完成上传、task 状态、SSE 流、审批、artifact、citation、trace panel、feedback 的用户可见闭环。
- 根据真实 Current 更新 architecture Markdown / HTML。
- PHASE12 做 full validation、program closure、history archive、commit、merge、push。

## Phase Definition of Done

### PHASE01 program-reopen-and-truth-source-freeze

完成条件：

- active program 明确是 `zuno-target-architecture-runtime-full-implementation-v1`。
- README、AGENTS、`.agent/programs/current.md`、`.agent/references/current-program.md` 不再指向旧 program。
- `只写 contract、schema 或 README 不能关闭 runtime phase` 成为 program/verifier/test 可见规则。
- 提交并推送。

### PHASE02 runtime-migration-map-and-repo-ownership-lock

完成条件：

- 有当前旧 runtime 路径到六层 target owner 的迁移矩阵。
- `platform/services/*`、`zuno.schema/*`、`zuno.database/*`、compat/vendor 的 owner、允许调用方向、冻结策略清楚。
- verifier/test 防止随意删除兼容路径或把 legacy 误写成 Current。
- 后续 runtime phase 的写入边界可执行。

### PHASE03 task-session-artifact-event-runtime

完成条件：

- 后端真实支持 workspace、knowledge space、session、uploaded file、ingest request、task、event stream、artifact、feedback 的生命周期。
- 同一个 task 能关联 `workspace_id`、`session_id`、`task_id`、`trace_id`、`artifact_id`、`feedback_id`。
- SSE 或等价事件流可测。
- focused API tests 通过。

### PHASE04 document-ingestion-parse-runtime

完成条件：

- Parse Gateway 有真实 runtime owner。
- 至少五类主格式进入 Canonical Document IR 或明确可复现 skip boundary。
- block/chunk/provenance/ACL/source metadata 可追踪。
- parser golden fixtures 可跑。

### PHASE05 index-jobs-and-knowledge-space-runtime

完成条件：

- Document IR 能进入 knowledge space index job。
- BM25 / vector / graph 至少一种真实可查询，另外两类有明确 runtime boundary 和 tests。
- index manifest、job status、retry/replay、failure state 可测。
- 上传文档后可检索，不停在 handoff contract。

### PHASE06 durable-single-controller-runtime

完成条件：

- Single Controller runtime 支持 durable checkpoint、resume、interrupt、approval wait、cancel、replan。
- runtime ledger 能回放关键状态。
- planning、retrieval、tool、answer、post-turn commit 事件进入 trace。
- 不引入产品默认多 Agent runtime。

### PHASE07 memory-db-and-context-governance

完成条件：

- MemoryEngine 接持久 store。
- raw event、task summary、approved durable memory、promotion/decay/consolidation 可测。
- memory 与 task/trace/source_event_ids 保持可追溯。
- sensitive memory 隔离和审查策略有 tests。

### PHASE08 tool-control-plane-approval-and-sandbox-runtime

完成条件：

- ToolCard registry、executor adapter、approval gate、credential broker boundary、sandbox profile、network policy 接运行时。
- 至少一组只读工具和一组高副作用工具走真实 approval/audit 路径。
- tool result normalization 进入 trace 和 task event stream。

### PHASE09 agentic-retrieval-evidence-citation-runtime

完成条件：

- Agentic retrieval 消费 PHASE04/05 的真实 index runtime。
- normal/enhanced/auto 产品模式可跑。
- basic/local/global/drift 内部方法至少形成可测选择路径。
- cited answer、EvidenceBundle、CitationBuilder、unsupported claim check 可测。

### PHASE10 security-observability-and-online-eval

完成条件：

- input、retrieval、tool、output gates 接真实运行时。
- ZunoSpan、本地 trace store、eval dataset、offline baseline、online sampling boundary 可跑。
- security/retrieval/answer/agent eval 能阻断 release gate 或生成失败证据。
- LangSmith-compatible export adapter 有可测路径；没有外部凭据时不能影响本地验证。

### PHASE11 web-desktop-surface-and-feedback-loop

完成条件：

- Web/Desktop 至少一个主 surface 完成真实用户闭环：上传、task 状态、事件流、citation、artifact、feedback。
- 审批、失败恢复、trace panel 或等价可视化有可用入口。
- 前端类型不是唯一交付；必须接后端 runtime。

### PHASE12 release-gate-full-e2e-closure

完成条件：

- 完整 vertical slice e2e 回放通过。
- parser golden、retrieval/eval/security baseline、repo verifier、focused pytest、必要 full pytest 通过或有用户批准的外部阻塞说明。
- `docs/architecture/architecture.md` 只把已验证能力写成 Current。
- `.agent/architecture/architecture.md` 与 docs 镜像一致。
- HTML 由同一个 Markdown 源生成并通过 check。
- program 归档到 `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/`。
- `.agent/programs/current.md` 进入 no-active 或下一 program 明确等待态。
- commit、merge、push 完成，并证明 main 与 origin/main 对齐。

## 每个 phase 的最小验证

每个 phase 结束前至少运行：

```powershell
git diff --check
python .agent/scripts/verify_agent_system.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
```

涉及 docs/architecture 时追加：

```powershell
python tools/agent/render_architecture.py --write
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
python .agent/scripts/verify_doc_boundaries.py
```

涉及 repo structure 时追加：

```powershell
python tools/scripts/verify_repo_structure.py
pytest -q tests/repo/test_repo_structure_consistency.py -p no:cacheprovider
```

涉及 runtime 时追加对应 focused tests，并优先新增失败测试再实现：

```powershell
pytest -q tests/agent tests/api tests/storage tests/retrieval tests/graphrag tests/evals -p no:cacheprovider
```

最终 PHASE12 必跑：

```powershell
git diff --check
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_repo_hygiene.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q -p no:cacheprovider
```

## Commit / Push / Merge 规则

- 每个 phase 或 worker 完成一个可验证切片后 commit。
- 每个 worker push 自己的 branch。
- 主线程集成后 push coordinator branch。
- PHASE12 后合并到 main，再 push main。
- 不强推、不 reset、不修改旧提交、不 revert 用户未要求的修改。
- 如果 worktree 有用户未说明修改，先停下来报告，不覆盖。
- 如果 GitHub HTTPS schannel TLS 失败，可以临时使用：

```powershell
git -c http.sslBackend=openssl push origin <branch-or-main>
```

## 停止条件

只有以下情况可以停止并请求用户决策：

- 工作树出现用户未说明且会被本轮覆盖的修改。
- 当前 program 文件和用户目标发生不可自动修复的事实冲突。
- 需要引入重型外部依赖、外部付费服务、删除 public compatibility path、改变 public API 兼容承诺。
- tests/verifier 连续失败，根因已定位且需要产品/架构取舍。
- 当前环境缺失不可替代的外部 binary 或凭据，且无法用本地可验证 adapter boundary 继续推进。

不要因为“任务大”“phase 多”“需要多步验证”就停在 PHASE01、PHASE02 或 contract-only closure。

## 最终交付格式

最终回答必须包含：

1. PHASE01-PHASE12 状态表。
2. 八类 runtime 交付物证据表。
3. 关键文件和目录变更。
4. 验证命令与结果。
5. 完整 vertical slice 回放证据。
6. remaining Target / Future，不得混入 Current。
7. program closure summary。
8. commit hash、merge hash、push status。
9. main 与 origin/main 对齐证明。

如果有未完成项，必须说明它为什么不属于本轮可安全完成范围，以及它被保留为 Target 还是 Future。
