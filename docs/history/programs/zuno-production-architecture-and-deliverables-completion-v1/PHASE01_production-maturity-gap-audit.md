# PHASE01 Production Maturity Gap Audit

status: completed

completed_at: 2026-07-01
next_phase: PHASE02_program-truth-source-and-execution-system

## 目标

对四大总交付物和八类 runtime-first 交付物做生产成熟度差距审计，形成可执行的 owner map、验证矩阵、外部依赖矩阵和停止条件。

## 范围

- 读取 `docs/architecture/production-readiness.md`、`docs/architecture/architecture.md`、`.agent/references/code-map.md`、`.agent/references/verification-map.md`。
- 核对 Web / Desktop、API、Agent Runtime、Memory、Tool、Knowledge、Security、Trace / Eval、repo governance 的 Current 证据。
- 标明每个 Production Target 属于本地可实现、需要外部服务、需要用户凭据、需要 Future program 或需要停止决策。

## 禁止范围

- 不修改 runtime 行为。
- 不把 Target 写成 Current。
- 不删除 compatibility、vendor、legacy alias 或 provider path。

## 验收闸门

- 产出成熟度差距表，覆盖四大总交付物和八类 runtime-first 交付物。
- 产出 owner map，指向具体目录、测试和 verifier。
- 产出 PHASE02-PHASE12 的执行优先级和停止条件。
- 更新本 phase 状态和后续 phase 入口。

## 验证命令

```powershell
git diff --check
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
python .agent/scripts/verify_agent_system.py
pytest -q tests/repo/test_agent_system.py tests/repo/test_repo_structure_consistency.py -p no:cacheprovider
```

## 需要先读取

- `docs/architecture/production-readiness.md`
- `docs/architecture/architecture.md`
- `docs/architecture/repo-ownership-matrix.md`
- `.agent/references/current-program.md`
- `.agent/references/code-map.md`
- `.agent/references/runtime-call-chain.md`
- `.agent/references/verification-map.md`
- `docs/history/programs/zuno-target-architecture-runtime-full-implementation-v1/closure-summary.md`

## 需要修改的文件

- `.agent/programs/PHASE01_production-maturity-gap-audit.md`
- `.agent/programs/implementation-roadmap.md`
- `.agent/programs/closure-checklist.md`
- 如发现事实源漂移：`README.md`、`AGENTS.md`、`.agent/references/current-program.md`、`docs/architecture/production-readiness.md`
- 如新增机器检查：`tools/scripts/verify_repo_structure.py`、`.agent/scripts/verify_agent_system.py`、`tests/repo/test_agent_system.py`、`tests/repo/test_repo_structure_consistency.py`

## 执行拆解

1. 建立四大总交付物审计表：Current 证据、Production Target、owner、测试入口、blocked 条件。
2. 建立八类 runtime-first 交付物审计表：产品闭环、解析索引、Agent Runtime、Memory、Tool/Sandbox、Knowledge/GraphRAG、Security/Eval、治理一致性。
3. 对每个 Production Target 标记执行类型：本地可实现、需要外部 adapter、需要真实服务、需要凭据、需要用户决策、应留作 Future。
4. 为 PHASE02-PHASE12 补执行优先级：先事实源和 governance，再 repo ownership，再 runtime productionization，最后 release closure。
5. 对每个 phase 列出最小可关闭证据，禁止只用 README 或 schema 关闭。

## 多 agent 分工

- Thread A：审计 docs / `.agent` / verifier / tests 的事实源一致性。
- Thread B：审计 `src/backend/zuno` 六层 owner、compatibility、vendor、legacy alias。
- Thread C：审计产品闭环、Desktop、API、artifact、trace、feedback。
- Thread D：审计 parse/index/GraphRAG/Memory/Tool/Security/Eval 的 production target。
- 主线程：合并差距表，决定后续 phase 顺序和停止条件。

## 需要返回的证据

- 四大总交付物 maturity gap 表。
- 八类 runtime-first delivery gap 表。
- owner map：每项指向目录、测试、verifier 和文档事实源。
- external dependency matrix：哪些需要真实服务、凭据或基础设施。
- PHASE02-PHASE12 执行风险排序。

## PHASE01 完成证据

本 phase 是生产成熟度差距审计 gate。它不修改 runtime 行为，不把 Target 写成 Current，只把后续 phase 的证据边界、owner、验证入口和停止条件写清。

启动证据：

- `git fetch --prune`：通过。
- `git status --short --branch`：`codex/zuno-truth-source-production-readiness-baseline...origin/codex/zuno-truth-source-production-readiness-baseline`，工作树干净。
- `git log --oneline -5 --decorate`：最新提交 `167d1cf6 docs: detail production completion phases`。

### 四大总交付物 maturity gap 表

| 总交付物 | Current 证据 | Production Target | owner / 事实源 | 执行类型 | 后续 phase / 停止条件 |
| --- | --- | --- | --- | --- | --- |
| 工作流自洽与自我维护 | `AGENTS.md`、`.agent/system.yaml`、`.agent/references/workflow*.md`、`.agent/templates/`、`.agent/programs/`、workflow verifier 和 repo tests 已形成基础闭环。 | 用户长期规则能被分类、写回、模板化并进入 verifier / tests；program open、phase closure、archive、docs sync 可持续自我检查。 | `AGENTS.md`、`.agent/references/workflow.md`、`.agent/references/workflow-governance.md`、`.agent/templates/`、`.agent/scripts/verify_agent_system.py`、`tests/repo/test_agent_system.py`。 | 本地可实现。 | PHASE02-PHASE03；如果规则只能靠对话记忆而无法进入 verifier/test，停止并回报。 |
| 文档系统清晰无冗余 | `docs/architecture/architecture.md` 负责总架构，`production-readiness.md` 负责成熟度，README / AGENTS / current-program 只做摘要，history 保存旧证据；architecture Markdown 与 Agent 镜像 hash 一致，两个 HTML 镜像 hash 一致。 | 前台文档持续少而精，架构、成熟度、program、history 各司其职；旧拆分入口不回流。 | `docs/architecture/README.md`、`docs/architecture/architecture.md`、`docs/architecture/production-readiness.md`、`.agent/architecture/architecture.md`、`.agent/references/docs-map.md`、`tools/agent/render_architecture.py`。 | 本地可实现。 | PHASE04；如果 Markdown / HTML / Agent mirror 生成结果不一致，停止修正生成源。 |
| 文件夹和代码 ownership 清晰 | `src/backend/zuno` 顶层六层已固定；`docs/architecture/repo-ownership-matrix.md`、legacy alias guard、compat / vendor guard、repo structure verifier 已存在。 | `platform/services`、compatibility、vendor、provider tree 不再显得零碎；compatibility 只做临时桥，不承担新 runtime owner。 | `docs/architecture/repo-ownership-matrix.md`、`.agent/references/code-map.md`、`.agent/references/runtime-call-chain.md`、`src/backend/zuno/**`、`tools/scripts/verify_repo_structure.py`、`.agent/scripts/verify_repo_hygiene.py`、legacy guard tests。 | 本地可实现，但 public import path 高风险。 | PHASE05；如果需要删除 public API、DB schema 或兼容路径才能推进，停止。 |
| 架构功能完整实现 | 第一版 runtime-first vertical slice 已有 Web 产品闭环、本地 parse / index / retrieval / tool / trace / eval surface、focused tests 和 release evidence。 | parser queue、深度解析、外部索引、LangGraph-compatible persistence、semantic/vector memory、真实 sandbox、vault、外部 trace/eval、Desktop、CI release gate。 | `docs/architecture/production-readiness.md`、`docs/architecture/architecture.md`、`src/backend/zuno/api|agent|memory|capability|knowledge|platform/**`、`tests/api|agent|knowledge|retrieval|graphrag|evals|frontend/**`。 | 本地 fallback + external adapter + blocked evidence 混合。 | PHASE06-PHASE12；外部服务、凭据或真实隔离运行时不可用时，只能写 adapter / fallback / Remaining Target，不能写 Current。 |

### 八类 runtime-first delivery gap 表

| runtime-first 交付物 | Current 证据 | Production Target | owner / tests | 执行类型 | 后续 phase |
| --- | --- | --- | --- | --- | --- |
| 产品闭环 | Web workspace Agent 已接 file / ingest / task / SSE / approval / artifact / trace-eval / feedback；后端 `WorkspaceTaskRuntimeService` 串起 durable runtime、index、security、trace 和 artifact。 | production Desktop 闭环、长任务恢复体验、下载与错误恢复产品化。 | `apps/web/**`、`apps/desktop/**`、`src/backend/zuno/api/services/workspace_task_runtime.py`、`tests/api/test_workspace_task_runtime.py`、`tests/api/test_workspace_product_loop_contract.py`、`tests/frontend/test_frontend_workspace_features.py`。 | 本地可实现；Desktop 打包环境可能 blocked。 | PHASE06 |
| 文档解析与索引 | `knowledge/ingestion` 与 `knowledge/indexing` 已有 Parse Gateway、Document IR、adapter registry、本地 BM25 / vector / graph index job、manifest、retry、replay。 | parser queue、OCR / layout / table / code 深度抽取、Docling / MinerU / Unstructured adapter、外部 Elasticsearch / Milvus / Neo4j 运维边界。 | `src/backend/zuno/knowledge/ingestion/**`、`src/backend/zuno/knowledge/indexing/**`、`tests/knowledge/**`、`tests/api/test_knowledge_api_contract.py`、`tests/retrieval/**`。 | local fallback + external adapter。 | PHASE07 |
| Agent Runtime | `SingleControllerDurableRuntime` 提供 checkpoint、interrupt、resume、cancel、failure snapshot，并接入 workspace task。 | 生产级 LangGraph-compatible persistence、进程重启恢复、approval wait/resume、cancel、exactly-once tool boundary。 | `src/backend/zuno/agent/durable_runtime.py`、`src/backend/zuno/api/services/workspace_task_runtime.py`、`tests/agent/**`、`tests/api/test_workspace_task_runtime.py`。 | 本地可实现；破坏性 DB schema 变更停止。 | PHASE08 |
| Memory 与 Context | `DatabaseMemoryStore`、`DurableMemoryStore`、`MemoryEngine`、governance ledger、promotion、decay、consolidation、Context Pack 已存在并接入 GeneralAgent。 | semantic/vector memory、后台 governance scheduler、隐私删除平台、memory eval baseline。 | `src/backend/zuno/memory/**`、`tests/agent/test_memory_*.py`、`tests/storage/**`。 | local deterministic fallback + external vector adapter。 | PHASE09 |
| Tool Control Plane 与 Sandbox | `ToolControlPlaneRuntime`、approval gate、credential ref、sandbox context、audit trace、tool event stream 已存在。 | rootless / gVisor / Firecracker sandbox、外部 vault / OAuth broker、网络代理、持久 approval DB。 | `src/backend/zuno/capability/**`、`src/backend/zuno/platform/security/**`、`tests/agent/test_capability_*.py`、`tests/api/test_workspace_security_observability_runtime.py`。 | adapter + local fallback；真实 sandbox / vault 可能 blocked。 | PHASE10 |
| Knowledge / GraphRAG / Evidence / Citation | `AgenticRetrievalRouter`、`EvidenceBundle`、`CitationBuilder`、`UnsupportedClaimChecker`、Agentic retrieval runtime 和本地 index runtime 已存在。 | GraphRAG extraction、community report、RRF / rerank、外部图索引、unsupported claim eval。 | `src/backend/zuno/knowledge/**`、`tests/graphrag/**`、`tests/retrieval/**`、`tests/evals/**`。 | local implementation + external graph adapter。 | PHASE11 |
| Security / Trace / Eval / Release | input / retrieval / tool / output gates、redaction、`ZunoSpan`、LangSmith-compatible export adapter、release baseline、trace replay surface 已存在。 | 生产 DLP、leakage 压测、外部 LangSmith / OTel sink、online eval、persistent trace store、CI release gate operations。 | `src/backend/zuno/platform/security/**`、`src/backend/zuno/platform/observability/**`、`tools/evals/zuno/**`、`tests/security/**`、`tests/evals/**`、`tests/api/test_workspace_security_observability_runtime.py`。 | local baseline + external adapter + blocked evidence。 | PHASE12 |
| 仓库治理与一致性 | 架构 Markdown / HTML 镜像、program front path、repo verifiers、focused tests、history archive 已存在。 | 持续发布治理、跨线程合并策略、生产运维证据自动归档。 | `AGENTS.md`、`.agent/system.yaml`、`.agent/programs/**`、`.agent/references/**`、`tools/scripts/**`、`.agent/scripts/**`、`tests/repo/**`。 | 本地可实现。 | PHASE02-PHASE05、PHASE12 |

### owner map 与验证矩阵

| 领域 | 当前 owner | 文档事实源 | 最小验证入口 |
| --- | --- | --- | --- |
| program truth / phase gate | `.agent/programs/**` | `.agent/programs/current.md`、`.agent/references/current-program.md` | `.agent/scripts/verify_agent_system.py`、`tests/repo/test_agent_system.py` |
| docs / architecture sync | `docs/architecture/**`、`.agent/architecture/**` | `docs/architecture/README.md`、`.agent/references/architecture-docs-map.md` | `python tools/agent/render_architecture.py --check`、`tools/scripts/verify_docs_entrypoints.py` |
| repo ownership / compatibility | `src/backend/zuno/**`、`platform/compatibility/**`、`platform/vendor/**` | `docs/architecture/repo-ownership-matrix.md`、`.agent/references/code-map.md` | `tools/scripts/verify_repo_structure.py`、`.agent/scripts/verify_repo_hygiene.py`、legacy guard tests |
| product workspace loop | `apps/web/**`、`apps/desktop/**`、`src/backend/zuno/api/**` | `docs/architecture/production-readiness.md`、`docs/architecture/architecture.md` | `tests/api/test_workspace_task_runtime.py`、`tests/frontend/test_frontend_workspace_features.py`、web tests |
| parse / index | `src/backend/zuno/knowledge/ingestion/**`、`src/backend/zuno/knowledge/indexing/**` | `docs/architecture/production-readiness.md`、`docs/architecture/repo-ownership-matrix.md` | `tests/knowledge/**`、`tests/api/test_knowledge_api_contract.py`、`tests/retrieval/**` |
| durable runtime | `src/backend/zuno/agent/**`、`src/backend/zuno/api/services/workspace_task_runtime.py` | `.agent/references/runtime-call-chain.md`、`docs/architecture/architecture.md` | `tests/agent/**`、`tests/api/test_workspace_task_runtime.py` |
| memory / context | `src/backend/zuno/memory/**` | `docs/architecture/production-readiness.md`、`.agent/references/code-map.md` | `tests/agent/test_memory_*.py`、`tests/storage/**` |
| tool / sandbox | `src/backend/zuno/capability/**`、`src/backend/zuno/platform/security/**` | `docs/architecture/production-readiness.md`、`.agent/references/code-map.md` | `tests/agent/test_capability_*.py`、`tests/api/test_workspace_security_observability_runtime.py` |
| GraphRAG / evidence / citation | `src/backend/zuno/knowledge/**` | `docs/architecture/architecture.md`、`docs/architecture/production-readiness.md` | `tests/graphrag/**`、`tests/retrieval/**`、`tests/evals/test_multihop_eval_real_runtime_runner.py` |
| security / trace / eval / release | `src/backend/zuno/platform/security/**`、`src/backend/zuno/platform/observability/**`、`tools/evals/zuno/**` | `docs/architecture/production-readiness.md`、`.agent/references/verification-map.md` | `tests/security/**`、`tests/evals/**`、PHASE12 full verification |

### external dependency matrix

| Target | Current 可做 | 需要外部服务 / 凭据 / 基础设施 | PHASE01 判断 |
| --- | --- | --- | --- |
| Docling / MinerU / Unstructured 深度 parser | adapter interface、local fallback、golden fixtures、blocked evidence | 真实 parser runtime、OCR/VLM 依赖、许可证确认 | 不写 Current；PHASE07 先落 adapter + fallback。 |
| Elasticsearch / Milvus / Neo4j | external index adapter、manifest、replay、local BM25/vector/graph fallback | 部署实例、连接配置、运维验证 | 不写 Current；PHASE07/PHASE11 保留 Remaining Target。 |
| LangGraph production checkpointer | LangGraph-compatible store contract、local persistence fallback | 生产 DB/checkpointer、进程重启验证环境 | 不替换 GeneralAgent；PHASE08 证明 restart/resume 边界。 |
| semantic/vector Memory DB | deterministic vector fallback、privacy delete contract、eval baseline | 外部向量库或 embedding service | 不写生产 Current；PHASE09 建 adapter 和隐私删除测试。 |
| rootless / gVisor / Firecracker sandbox | sandbox profile、policy、audit trace、local deterministic sandbox | 本机真实隔离 runtime、权限、网络策略 | 不写真实隔离 Current；PHASE10 记录 blocked evidence。 |
| external vault / OAuth broker | credential ref contract、dev broker fallback、no-secret repo guard | 真实 vault/OAuth app、用户凭据 | 不保存 secret；PHASE10 只写 ref + fallback。 |
| LangSmith / OTel external sink | OTel-compatible span、redacted export payload、local release baseline | sink endpoint、token、在线 eval 平台 | 不把本地 baseline 写成在线平台；PHASE12 写 adapter + blocked evidence。 |
| Desktop production packaging | API/bridge contract、Desktop source audit、local smoke evidence | 打包依赖、签名/发布环境 | PHASE06 可做 contract / local fallback；缺少环境时保留 Remaining Target。 |

### PHASE02-PHASE12 执行风险排序

| phase | 优先级 | 主要风险 | 最小可关闭证据 |
| --- | --- | --- | --- |
| PHASE02 | P0 | current_phase、phase 文件、verifier/test 期望硬编码导致每次 phase 转移都要同步；thread prompt 规则与本轮单线程目标可能漂移。 | active program 文件清单、phase gate verifier/test、单线程挂机边界写清。 |
| PHASE02 | P0 | `.agent/system.yaml` docs-agent route 和 PHASE02 验证命令需要明确是否纳入 `python tools/scripts/verify_docs_entrypoints.py`；该 verifier 是 production-readiness 摘要边界和 retired front-path 的关键 guard。 | verify-command truth source、route verify list、PHASE02 验证命令和 repo tests 对齐。 |
| PHASE03 | P0 | 长期规则只停留在对话或单个文档，模板/verifier 未覆盖。 | workflow 规则分类表、写回路径、template boundary test/verifier。 |
| PHASE04 | P1 | README / AGENTS / architecture / production-readiness 重复展开导致双事实源。 | 文档职责表、render_architecture --check、docs entrypoint tests。 |
| PHASE05 | P1 | compatibility/vendor/public alias 删除风险高，可能破坏 legacy import。 | import matrix、low-risk migration diff、legacy guard 和 structure verifier。 |
| PHASE06 | P2 | Desktop 与 Web contract 不一致；长任务恢复可能依赖 PHASE08 durable runtime。 | Web/Desktop task lifecycle contract、focused API/frontend tests、blocked evidence。 |
| PHASE07 | P2 | 外部 parser/index 服务不可用；深度抽取依赖许可证或环境。 | parser queue/job contract、local fallback fixtures、external adapter Remaining Target。 |
| PHASE08 | P1 | exactly-once tool boundary 与 durable task persistence 会影响 PHASE06/10/12；破坏性 DB schema 是停止条件。 | checkpoint/resume/cancel/approval tests、failure snapshot、ledger proof。 |
| PHASE09 | P2 | semantic/vector memory 与隐私删除容易冲突；外部向量库不可用。 | memory taxonomy、local vector fallback、privacy delete tests、eval baseline。 |
| PHASE10 | P2 | 真实 sandbox/vault/network 依赖外部环境；高副作用工具必须强制 approval。 | tool risk matrix、approval flow、credential ref、sandbox adapter boundary、audit trace tests。 |
| PHASE11 | P2 | citation 无 evidence、enhanced/auto 绕过 unsupported claim guard、外部图服务不可用。 | retrieval mode matrix、evidence bundle trace、unsupported claim metrics、focused eval tests。 |
| PHASE12 | P0 | 未完成 phase 被归档、full verification 失败、外部 eval 被伪装成 Current。 | 四大/八类 closure table、Current/Remaining Target/Future 边界、archive、full verification log、commit/push/main-origin proof。 |

### 验证结果

PHASE01 closure 已运行最小有效验证，并追加 architecture/docs 相关检查，因为本 phase 更新了 `docs/architecture/architecture.md` 和生成镜像。

| Command | Result |
| --- | --- |
| `git diff --check` | pass；仅报告 Windows LF/CRLF working-copy warning。 |
| `python tools/agent/render_architecture.py --check` | pass；architecture Markdown mirror 和两个 HTML 输出与 `docs/architecture/architecture.md` 同步。 |
| `python tools/scripts/verify_docs_entrypoints.py` | pass。 |
| `python tools/scripts/verify_repo_structure.py` | pass。 |
| `python .agent/scripts/verify_agent_system.py` | pass。 |
| `pytest -q tests/repo/test_agent_system.py tests/repo/test_repo_structure_consistency.py tests/repo/test_docs_entrypoints.py -p no:cacheprovider` | `51 passed in 2.09s`。 |

## 停止条件

- Current / Target 边界冲突，无法判断某能力是否已由代码和测试证明。
- 发现需要删除 public API、数据库 schema 或兼容路径才能继续。
- 发现生产级目标需要真实外部凭据且无法用 adapter / local fallback 表达。
