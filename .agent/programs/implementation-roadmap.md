# Zuno Master Architecture Implementation V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 先整理 Zuno 项目文件夹和代码分布，再按八个方面交付企业私有知识库 Agent Workspace 的目标架构落地，并同步正式架构 Markdown、架构 HTML、README、verifier、tests 和历史归档。

**Architecture:** 本 program 保持 Zuno 近期产品 runtime 为 Single Controller Agent，不把 Codex 多线程交付方式误写成产品多 Agent 架构。实施顺序是 repo/code ownership baseline -> enterprise product loop -> ingestion -> runtime -> memory -> tool plane -> RAG/GraphRAG -> security -> eval/observability -> architecture docs/html -> release closure。每个 phase 都必须区分 Current / Target / Future，并用 tests/verifier/trace/eval 证明后再升级 Current。

**Tech Stack:** Python、FastAPI、LangGraph-compatible runtime、GraphRAG、BM25/vector retrieval、MCP、Markdown、Mermaid、LangSmith-compatible trace/eval、pytest、Zuno repo verifiers、`.agent/programs` lifecycle。

---

state: active
program: zuno-master-architecture-implementation-v1
current_phase: PHASE03_enterprise-scenario-and-product-loop

每次新 program 都从 `PHASE01` 开始编号。

## 第一性原则

这不是“再写一份架构规划”。本 program 的目标是让仓库从外观、代码目录、运行时能力、评测证据和展示文档五个方向一起变成熟。

先整理文件夹，是因为当前顶层六层已经清楚，但 `platform/services`、`capability/tools`、`capability/mcp/servers`、`platform/compatibility` 和旧 import alias 仍让读者觉得零碎。没有 ownership matrix 和兼容矩阵，后续 runtime feature 会继续堆在旧位置。

## 八个方面目标产物矩阵

下表是本 program 的目标产物，不是当前完成事实。每一项只有在对应 phase 的 tests、verifier、eval evidence 或可复现 trace 通过后，才能写入 Current。

| 产物 | 产物名称 | 主要路径 | 验收方式 |
| --- | --- | --- | --- |
| D1 | 项目文件夹与代码布局治理 | `src/backend/zuno/**`, `tools/scripts/verify_repo_structure.py`, `tests/repo/*` | layout audit、ownership matrix、no-cache proof、compat import matrix、repo structure tests。 |
| D2 | 企业私有知识库场景与产品闭环 | `docs/architecture/architecture.md`, `src/backend/zuno/api/**`, `apps/web/**` | workspace/task/session/upload/artifact/event flow contract tests 和架构图更新。 |
| D3 | Document Ingestion / Parse Gateway | `src/backend/zuno/knowledge/ingestion/**`, parser tests | PDF/Office/image/code/text parser matrix、Canonical Document IR、chunk/provenance tests。 |
| D4 | Single Controller Agent Runtime | `src/backend/zuno/agent/**`, runtime tests | `prepare_context -> plan -> ReAct -> observe -> reflect -> replan -> post_turn_commit` 最小可运行链。 |
| D5 | Context / Memory 系统 | `src/backend/zuno/memory/**`, memory tests | Raw Event Log、Recent Window、Summary、Structured Memory、promotion/decay tests。 |
| D6 | Tool Control Plane | `src/backend/zuno/capability/**`, tool tests | ToolCard manifest、selector、policy、approval、executor adapter、MCP/sandbox tests。 |
| D7 | RAG / GraphRAG 知识系统 | `src/backend/zuno/knowledge/**`, retrieval/eval tests | basic/local/global/drift、fusion、GraphRAG extraction/query、evidence/citation tests。 |
| D8 | Trust / Eval / Observability / Docs 展示闭环 | `src/backend/zuno/platform/**`, `docs/architecture/**`, `.agent/architecture/**` | Security gates、LangSmith-compatible trace/eval、architecture.md/html 同步、release gate。 |

## 与旧八大交付物的关系

上一轮 `zuno-eight-deliverables-full-realization-v1` 证明的是文档系统、元工作流、模板/计划、架构文档、HTML 展示、目标架构表达、代码目录边界和一致性验证的闭环。本 program 继承这些机制，但把重心转到“产品运行时与工程结构落地”：

- 归档路径：`docs/history/programs/zuno-eight-deliverables-full-realization-v1/`

- 旧交付物 1-3：继续由 `.agent/`、templates、program lifecycle 维护。
- 旧交付物 4-6：由 PHASE11 更新 `docs/architecture/architecture.md`、`.agent/architecture/architecture.md` 和 HTML。
- 旧交付物 7：由 PHASE02 先做代码目录治理，再贯穿 runtime phases。
- 旧交付物 8：由每个 phase 的 focused tests 和 PHASE12 release gate 维护。

## 文件结构

本 program 的前台状态文件：

- Modify: `.agent/programs/README.md`
- Modify: `.agent/programs/current.md`
- Modify: `.agent/programs/implementation-roadmap.md`
- Modify: `.agent/programs/closure-checklist.md`
- Create: `.agent/programs/PHASE01_program-baseline-and-previous-closure.md`
- Create: `.agent/programs/PHASE02_project-folder-and-code-layout-cleanup.md`
- Create: `.agent/programs/PHASE03_enterprise-scenario-and-product-loop.md`
- Create: `.agent/programs/PHASE04_document-ingestion-parse-gateway.md`
- Create: `.agent/programs/PHASE05_agent-runtime-langgraph-harness.md`
- Create: `.agent/programs/PHASE06_context-memory-system.md`
- Create: `.agent/programs/PHASE07_tool-control-plane-mcp-approval.md`
- Create: `.agent/programs/PHASE08_rag-graphrag-evidence-citation.md`
- Create: `.agent/programs/PHASE09_security-governance-sandbox.md`
- Create: `.agent/programs/PHASE10_eval-observability-langsmith.md`
- Create: `.agent/programs/PHASE11_architecture-docs-html-refresh.md`
- Create: `.agent/programs/PHASE12_validation-release-closure.md`

Program state and governance surfaces:

- Modify: `.agent/references/current-program.md`
- Modify: `.agent/system.yaml`
- Modify: `.agent/scripts/verify_agent_system.py`
- Modify: `.agent/scripts/verify_doc_boundaries.py`
- Modify: `.agent/scripts/verify-workflow.ps1`
- Modify: `tools/scripts/verify_repo_structure.py`
- Modify: `tests/repo/test_agent_system.py`
- Modify: `tests/repo/test_repo_structure_consistency.py`
- Modify: `tests/repo/test_publish_boundary.py`
- Modify: `README.md`
- Modify: `AGENTS.md`

Research archive surfaces:

- Create/Modify: `docs/history/research/README.md`
- Create/Modify: `docs/history/research/chatgpt-research-mode-artifacts/README.md`
- Archive: `docs/history/research/chatgpt-research-mode-artifacts/zuno-enterprise-private-knowledge-agent-workspace-target-architecture-research-2026-06-30.pdf`
- Extract: `docs/history/research/chatgpt-research-mode-artifacts/zuno-enterprise-private-knowledge-agent-workspace-target-architecture-research-2026-06-30.md`
- Archive: `docs/history/research/chatgpt-research-mode-artifacts/zuno-target-architecture-deep-research-implementation-blueprint-2026-06-30.pdf`
- Archive: `docs/history/research/chatgpt-research-mode-artifacts/zuno-target-architecture-deep-research-implementation-blueprint-2026-06-30.md`
- Copy: `docs/architecture/assets/zuno-target-architecture-deep-research-implementation-blueprint-2026-06-30.pdf`

Architecture surfaces:

- Modify: `docs/architecture/architecture.md`
- Generate: `docs/architecture/architecture.html`
- Mirror: `.agent/architecture/architecture.md`
- Mirror: `.agent/architecture/architecture.html`
- Modify: `docs/architecture/README.md`
- Modify: `.agent/architecture/README.md`

Runtime implementation paths opened by later phases:

- Modify/Create: `src/backend/zuno/knowledge/ingestion/**`
- Modify/Create: `src/backend/zuno/agent/**`
- Modify/Create: `src/backend/zuno/memory/**`
- Modify/Create: `src/backend/zuno/capability/**`
- Modify/Create: `src/backend/zuno/knowledge/**`
- Modify/Create: `src/backend/zuno/platform/security/**`
- Modify/Create: `src/backend/zuno/platform/observability/**`
- Modify/Create: `tools/evals/zuno/**`
- Modify/Create: `tests/**`

## Phase Overview

| Phase | 状态 | 交付重点 |
| --- | --- | --- |
| PHASE01 | completed | 收口上一轮架构计划，打开本大型 program，固定 active 状态和 verifier。 |
| PHASE02 | completed | 项目文件夹、代码 ownership、compat/vendor、缓存和 repo structure 治理。 |
| PHASE03 | active | 企业知识库场景、workspace、task/session、upload/artifact/event flow。 |
| PHASE04 | pending | Document Ingestion / Parse Gateway 和多格式解析矩阵。 |
| PHASE05 | pending | Single Controller Agent Runtime / LangGraph-compatible harness。 |
| PHASE06 | pending | Context / Memory read-write-manage 系统。 |
| PHASE07 | pending | Tool Control Plane、MCP、approval、executor adapter、sandbox。 |
| PHASE08 | pending | RAG/GraphRAG、retrieval fusion、evidence/citation。 |
| PHASE09 | pending | Security governance、DLP、prompt injection 防护、sandbox。 |
| PHASE10 | pending | LangSmith-compatible trace/eval、offline/online eval、CI gate。 |
| PHASE11 | pending | 架构 Markdown、HTML、README、图集和展示文档更新。 |
| PHASE12 | pending | 全量验证、release baseline、归档和推送。 |

## Phase Dependency Gates

| Gate | 依赖 | 被阻塞的 phase | 硬规则 |
| --- | --- | --- | --- |
| G1: ownership baseline | PHASE02 ownership matrix、compat/vendor 边界、repo structure guard。 | PHASE03-PHASE10 代码实现。 | 任何新增 runtime 代码必须先能说明 target owner，不能继续堆进 `platform/services` 或 compatibility。 |
| G2: product task model | PHASE03 task/session/artifact/event contract。 | PHASE05 runtime、PHASE10 trace/eval、PHASE12 closure。 | Runtime、trace、artifact 必须共享 task_id / session_id / trace_id。 |
| G3: Document IR | PHASE04 Canonical Document IR、parser matrix、source span。 | PHASE08 GraphRAG / Evidence / Citation、PHASE09 DLP、PHASE10 retrieval eval。 | GraphRAG、citation、DLP 不直接消费 parser 原始输出，只消费统一 IR 或 handoff payload。 |
| G4: runtime state | PHASE05 state model、node contract、event stream。 | PHASE06 memory、PHASE07 tool approval、PHASE09 interrupt/resume。 | Memory、tool、security 必须挂在同一个 runtime state / trace 上。 |
| G5: ToolCard risk | PHASE07 ToolCard v1、side-effect matrix、executor adapter。 | PHASE09 sandbox、PHASE10 tool trajectory eval。 | 高风险工具没有 ToolCard policy 不允许上线。 |
| G6: evidence contract | PHASE08 EvidenceBundle、Citation Builder、unsupported claim check。 | PHASE10 faithfulness / citation eval、PHASE11 Current 更新。 | 没有 evidence/citation 证据的 GraphRAG 能力不能写成成熟 Current。 |
| G7: security gate | PHASE09 input/retrieval/tool/output gates。 | PHASE10 online eval、PHASE12 release closure。 | 高风险动作 approval escape 必须为 0。 |
| G8: eval baseline | PHASE10 dataset、metric thresholds、release baseline。 | PHASE11/PHASE12。 | 文档更新 Current 前必须有 eval 或 focused test 证据。 |

## Execution Model

本 program 可以使用主线程挂机模式，也可以拆成多 worktree 并行模式。若并行，推荐 workstreams：

- A 线：`codex/zuno-architecture-doc-v2`，只碰 `docs/architecture/**`、`.agent/architecture/**`、少量 README / verifier，目标是把最新研究报告的九平面、十图、架构说明和 HTML 展示吸收进正式文档。
- B 线：`codex/zuno-code-layout-rationalization-v1`，主要碰 `src/backend/zuno/**`、repo verifiers 和 repo tests，目标是 ownership matrix、compat 收缩、platform/services 瘦身、capability 内部归类和目标代码树 guard。
- C 线：`codex/zuno-document-ingestion-v1`，集中在 `src/backend/zuno/knowledge/ingestion/**` 和 parser tests，目标是 parser router、Canonical Document IR、Docling / PyMuPDF4LLM / MinerU / Unstructured / native parser adapter、chunk/provenance/ACL。
- D 线：`codex/zuno-runtime-memory-tool-plane-v1`，集中在 `src/backend/zuno/agent/**`、`src/backend/zuno/memory/**`、`src/backend/zuno/capability/**`，目标是 LangGraph-compatible runtime harness、Context Builder、ToolCard Registry、selector / policy / approval。
- E 线：`codex/zuno-security-sandbox-v1`，集中在 `src/backend/zuno/platform/security/**`、tool policy 和 sandbox tests，目标是 Policy Sandbox、Workspace Sandbox、Execution Sandbox、Network / Credential Sandbox。
- F 线：`codex/zuno-eval-observability-v1`，集中在 `src/backend/zuno/platform/observability/**`、`tools/evals/zuno/**` 和 eval tests，目标是 OTel-compatible span schema、LangSmith sink、offline / online eval、CI regression gate。

共享文件如 `AGENTS.md`、`.agent/system.yaml`、`docs/architecture/architecture.md`、`tools/scripts/verify_repo_structure.py` 和核心 repo tests 由主线程最终收口。

并行执行规则：每条线必须在独立 worktree + 独立 `codex/` 分支上工作；主线程负责 current-program 状态、架构源文档、verifier、tests 和 final integration。禁止多条线同时大改同一个热点目录。若某条线只处理局部目录，可以启用 sparse-checkout 降低扫描面，但不能改变仓库事实源。

可并行性规则：

- PHASE02 是所有 runtime 代码移动和新增目录的前置门，不能跳过。
- PHASE03 和 PHASE04 可以在 PHASE02 ownership baseline 后并行，但 PHASE05 必须读取 PHASE03 的 task/session contract。
- PHASE06、PHASE07、PHASE08 可以在 PHASE05 state model 固定后分工并行，但都必须写入同一 trace/span contract。
- PHASE09 依赖 PHASE07 ToolCard risk matrix 和 PHASE03 workspace scope。
- PHASE10 可以提前设计 schema，但 release gate 阈值必须等 PHASE08/09 的输出字段固定。
- PHASE11 和 PHASE12 由主线程收口，不建议分给独立 worker 直接修改 shared architecture source。

## Verification Baseline

每个 phase 至少运行自身 focused tests。PHASE12 必跑：

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

## Task 1: Program Baseline And Previous Closure

Status: completed

**Files:**
- Modify: `.agent/programs/current.md`
- Modify: `.agent/programs/README.md`
- Modify: `.agent/programs/implementation-roadmap.md`
- Modify: `.agent/programs/closure-checklist.md`
- Modify: `.agent/references/current-program.md`
- Modify: `README.md`
- Modify: `AGENTS.md`
- Modify: `.agent/scripts/verify_agent_system.py`
- Modify: `tools/scripts/verify_repo_structure.py`
- Modify: `tests/repo/test_agent_system.py`
- Modify: `tests/repo/test_repo_structure_consistency.py`
- Archive: `docs/history/programs/zuno-architecture-detail-and-execution-plan-v1/`

- [ ] **Step 1: Confirm branch and clean working tree**

Run:

```powershell
git status --short --branch
```

Expected: branch starts with `codex/` and no unrelated dirty files exist.

- [ ] **Step 2: Archive previous architecture-detail program**

Move the previous `.agent/programs` files to:

```text
docs/history/programs/zuno-architecture-detail-and-execution-plan-v1/
```

Expected: `.agent/programs/` contains only this program after new files are written.

- [ ] **Step 3: Open the new active program**

Set these state values in `.agent/programs/current.md`, `.agent/programs/implementation-roadmap.md`, `.agent/references/current-program.md`, README and AGENTS:

```text
program: zuno-master-architecture-implementation-v1
state: active
current_phase: PHASE03_enterprise-scenario-and-product-loop
```

- [ ] **Step 4: Archive ChatGPT research mode artifacts**

Archive the user-provided target architecture research report under:

```text
docs/history/research/chatgpt-research-mode-artifacts/
```

Expected:

```text
README.md
zuno-enterprise-private-knowledge-agent-workspace-target-architecture-research-2026-06-30.pdf
zuno-enterprise-private-knowledge-agent-workspace-target-architecture-research-2026-06-30.md
zuno-target-architecture-deep-research-implementation-blueprint-2026-06-30.pdf
zuno-target-architecture-deep-research-implementation-blueprint-2026-06-30.md
```

The PDF is the preserved original. The Markdown file is the extracted research input used to expand architecture docs and future implementation plans.

Also keep the latest blueprint PDF under:

```text
docs/architecture/assets/zuno-target-architecture-deep-research-implementation-blueprint-2026-06-30.pdf
```

This copy is an architecture attachment for human readers. It is not a second architecture source of truth.

- [ ] **Step 5: Update active-program verifiers**

Update `.agent/scripts/verify_agent_system.py`, `tools/scripts/verify_repo_structure.py`, `tests/repo/test_agent_system.py`, `tests/repo/test_repo_structure_consistency.py`, `tests/repo/test_publish_boundary.py` to recognize PHASE01-PHASE12.

- [ ] **Step 6: Run program-state verification**

Run:

```powershell
python .agent/scripts/verify_agent_system.py
python tools/scripts/verify_repo_structure.py
pytest -q tests/repo/test_agent_system.py tests/repo/test_repo_structure_consistency.py tests/repo/test_publish_boundary.py -p no:cacheprovider
```

Expected: all pass.

## Task 2: Project Folder And Code Layout Cleanup

Status: active

**Files:**
- Modify: `src/backend/zuno/**`
- Modify: `src/backend/zuno/*/README.md`
- Modify: `tools/scripts/verify_repo_structure.py`
- Modify: `.agent/scripts/verify_repo_hygiene.py`
- Modify: `tests/repo/test_repo_structure_consistency.py`
- Modify: `tests/legacy_guards/test_zuno_alias_imports.py`
- Modify: `docs/architecture/architecture.md`

- [ ] **Step 1: Produce ownership matrix**

Create or update a code ownership table covering:

```text
api -> HTTP routes, DTO, request/response contracts
agent -> Single Controller Agent runtime and harness
memory -> context, memory contracts, storage policy
capability -> ToolCard, selector, policy, executor metadata
knowledge -> ingestion, retrieval, GraphRAG, evidence, citation
platform -> DB, storage, queue, model gateway, vendor, infrastructure
compat -> legacy import registration only
```

- [ ] **Step 2: Remove local cache noise**

Remove untracked `__pycache__`, `.pytest_cache`, local output and temp directories from the workspace. Do not delete tracked source files.

Run:

```powershell
git ls-files | rg "__pycache__|\\.pyc$"
```

Expected: no tracked Python cache files.

- [ ] **Step 3: Split compat responsibility**

Keep legacy import behavior, but separate three meanings:

```text
legacy import registry -> import alias compatibility
vendor -> vendored packages such as fastapi_jwt_auth
business/runtime code -> never placed in compatibility
```

No compatibility move is accepted until `tests/legacy_guards/test_zuno_alias_imports.py` passes.

- [ ] **Step 4: Thin visual clutter in provider/tool trees**

Classify `capability/tools`, `capability/mcp/servers`, and `platform/services` into:

```text
current runtime owner
target owner
compat-only import
provider implementation
candidate for archive
```

Do not move provider trees in the same commit as runtime behavior changes.

## Task 3: Enterprise Scenario And Product Loop

Status: pending

**Files:**
- Modify/Create: `src/backend/zuno/api/**`
- Modify/Create: `src/backend/zuno/platform/services/workspace/**`
- Modify/Create: `apps/web/**`
- Modify: `docs/architecture/architecture.md`
- Test: `tests/api/**`
- Test: `tests/frontend/**`

- [ ] **Step 1: Define product objects**

Define contracts for:

```text
Workspace
Knowledge Space
Session
Task
Uploaded File
Artifact
Trace Event
Citation
User Feedback
```

- [ ] **Step 2: Define event flow**

Document and test the product loop:

```text
upload -> parse/index -> ask -> stream trace -> answer/report -> artifact download -> feedback/eval
```

- [ ] **Step 3: Keep frontend scope explicit**

Frontend work in this phase only implements product visibility for the scenario loop. It does not create unrelated landing pages or decorative marketing screens.

## Task 4: Document Ingestion / Parse Gateway

Status: pending

**Files:**
- Create/Modify: `src/backend/zuno/knowledge/ingestion/**`
- Modify: `src/backend/zuno/knowledge/README.md`
- Test: `tests/knowledge/**`
- Test: `tests/api/**`
- Docs: `docs/architecture/architecture.md`

- [ ] **Step 1: Define Canonical Document IR**

The IR must carry:

```text
document_id
workspace_id
source_uri
mime_type
parser_name
parser_version
blocks
tables
figures
page_or_slide
line_range
bbox
acl_scope
provenance
```

- [ ] **Step 2: Define parser matrix**

Minimum supported classes:

```text
PDF
DOCX
PPTX
XLSX
TXT
MD
CSV
JSON
HTML
images / scanned documents
code files
```

- [ ] **Step 3: Route parser output to indexes**

Accepted ingestion output must support:

```text
BM25 index payload
vector embedding payload
GraphRAG entity/relation extraction payload
evidence/citation anchor payload
```

## Task 5: Agent Runtime / LangGraph Harness

Status: pending

**Files:**
- Modify/Create: `src/backend/zuno/agent/**`
- Modify/Create: `tests/agent/**`
- Modify: `docs/architecture/architecture.md`

- [ ] **Step 1: Define runtime state**

The state model must include:

```text
thread_id
workspace_id
goal
context_pack
plan
current_step
observations
tool_calls
retrieval_events
approval_interrupts
trace_id
memory_candidates
artifact_refs
```

- [ ] **Step 2: Implement minimal loop contract**

Target contract:

```text
prepare_context -> plan -> ReAct step -> observe -> reflect -> replan/continue/finish -> post_turn_commit
```

- [ ] **Step 3: Keep LangGraph boundary honest**

LangGraph is an implementation candidate for state graph, checkpoint, streaming, interrupt and resume. It is not the planning module itself.

## Task 6: Context / Memory System

Status: pending

**Files:**
- Modify/Create: `src/backend/zuno/memory/**`
- Modify/Create: `tests/agent/test_memory_*.py`
- Modify: `docs/architecture/architecture.md`

- [ ] **Step 1: Separate memory layers**

Implement or formalize:

```text
Raw Event Log
Working Context
Recent Window
Task Summary
Structured Long-term Memory
Graph Memory candidate
Context Pack renderer
```

- [ ] **Step 2: Define write path**

Post-turn memory flow:

```text
raw events -> extraction candidate -> dedupe/conflict check -> review -> promote / decay / discard
```

- [ ] **Step 3: Define memory eval**

Memory tests must cover relevance, over-retention, sensitive data redaction and stale memory suppression.

## Task 7: Tool Control Plane / MCP / Approval

Status: pending

**Files:**
- Modify/Create: `src/backend/zuno/capability/**`
- Modify/Create: `tests/agent/test_capability_*.py`
- Modify/Create: `tests/tools/**`
- Modify: `docs/architecture/architecture.md`

- [ ] **Step 1: Define ToolCard manifest**

Tool metadata must include:

```text
name
description
input_schema
output_schema
owner
execution_mode
side_effect_level
approval_required
sandbox_required
network_policy
credential_policy
audit_required
```

- [ ] **Step 2: Define executor adapters**

Execution modes:

```text
local_function
local_sdk
sdk_to_api
api
local_cli
cli_to_api
ssh
mcp_local
mcp_remote
sandbox
```

- [ ] **Step 3: Add approval gate contract**

High-side-effect tools such as email send, external write, SSH, delete, overwrite and unrestricted CLI must require interrupt/approval/audit.

## Task 8: Agentic GraphRAG / Evidence / Citation

Status: pending

**Files:**
- Modify/Create: `src/backend/zuno/knowledge/**`
- Modify/Create: `src/backend/zuno/platform/services/graphrag/**` during migration slices
- Modify/Create: `tests/graphrag/**`
- Modify/Create: `tests/retrieval/**`
- Modify/Create: `tests/evals/**`
- Modify: `docs/architecture/architecture.md`

- [ ] **Step 1: Preserve user-facing product mode contract**

Product modes:

```text
normal -> force basic
enhanced -> retrieval required, Agentic Retrieval Router selects method(s)
auto -> Agent first decides if retrieval is needed, then selects method(s)
```

- [ ] **Step 2: Preserve internal query method contract**

Resolved query methods:

```text
basic
local
global
drift
```

`auto` is never a final resolved query method.

- [ ] **Step 3: Add Agentic Retrieval Router contract**

Router input must include product mode, user query, workspace scope, context pack, ACL scope, budget, evidence state and fallback history. Router output must include candidate methods, resolved method(s), route reason, fallback reason and trace metadata.

- [ ] **Step 4: Implement staged fusion**

`global` acts as community-level prior. It must not be flattened directly into BM25 chunk ranking without evidence-stage design.

## Task 9: Security / Governance / Sandbox

Status: pending

**Files:**
- Modify/Create: `src/backend/zuno/platform/security/**`
- Modify/Create: `src/backend/zuno/capability/policy.py`
- Modify/Create: `tests/security/**`
- Modify/Create: `tests/tools/**`
- Modify: `docs/architecture/architecture.md`

- [ ] **Step 1: Define four security gates**

```text
input gate -> auth, file validation, PII/business secret scan, prompt injection scan
retrieval gate -> ACL, workspace scope, trust label, chunk sanitization
tool gate -> side-effect policy, approval, timeout, cwd/network/credential scope
output gate -> DLP, citation coverage, format validation, redaction
```

- [ ] **Step 2: Define sandbox levels**

```text
policy sandbox
workspace sandbox
execution sandbox
network / credential sandbox
```

- [ ] **Step 3: Add security eval cases**

Security regression must include prompt injection, indirect prompt injection, secret exfiltration, cross-workspace leakage and unauthorized tool call attempts.

## Task 10: Eval / Observability / LangSmith

Status: pending

**Files:**
- Modify/Create: `src/backend/zuno/platform/observability/**`
- Modify/Create: `tools/evals/zuno/**`
- Modify/Create: `tests/evals/**`
- Modify: `docs/evidence/eval-baselines.md`
- Modify: `docs/architecture/architecture.md`

- [ ] **Step 1: Define trace schema**

Trace fields:

```text
trace_id
thread_id
workspace_id
user_id
product_mode
requested_query_method
resolved_query_method
model
tokens
latency_ms
cost
tool_calls
retrieval_events
evidence_count
citation_coverage
approval_events
sandbox_events
security_events
failure_reason
```

- [ ] **Step 2: Define eval layers**

```text
retrieval eval
answer eval
agent trajectory eval
security eval
business scenario eval
```

- [ ] **Step 3: Keep local gate and LangSmith adapter**

Local pytest/eval runners remain release gates. LangSmith-compatible export is a target sink, not the only source of truth.

## Task 11: Architecture Docs / HTML Refresh

Status: pending

**Files:**
- Modify: `docs/architecture/architecture.md`
- Generate: `docs/architecture/architecture.html`
- Mirror: `.agent/architecture/architecture.md`
- Mirror: `.agent/architecture/architecture.html`
- Modify: `README.md`
- Modify: `AGENTS.md`
- Modify: `.agent/references/diagram-inventory.md`

- [ ] **Step 1: Update Current / Target facts**

Only completed and verified phase outputs move to Current. Unimplemented runtime target remains Target.

- [ ] **Step 2: Update diagrams**

Architecture HTML must show:

```text
enterprise knowledge scenario
folder/code ownership
document ingestion
agent runtime loop
memory system
tool control plane
RAG/GraphRAG
security/sandbox
trace/eval
release governance
```

- [ ] **Step 3: Regenerate HTML**

Run:

```powershell
python tools/agent/render_architecture.py --write
python tools/agent/render_architecture.py --check
```

Expected: both pass and docs/agent mirrors are byte-consistent.

## Task 12: Validation / Release Closure

Status: pending

**Files:**
- Modify: `.agent/programs/closure-checklist.md`
- Modify: `.agent/references/current-program.md`
- Modify: `README.md`
- Modify: `AGENTS.md`
- Archive: `docs/history/programs/zuno-master-architecture-implementation-v1/`

- [ ] **Step 1: Run full verification**

Run:

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

- [ ] **Step 2: Write closure evidence**

Closure summary must include:

```text
phase completion table
eight deliverables evidence table
verification commands and results
known remaining Target/Future items
commit hash
branch name
push status
```

- [ ] **Step 3: Archive completed program**

When complete, move `.agent/programs` phase files to:

```text
docs/history/programs/zuno-master-architecture-implementation-v1/
```

Then set `.agent/programs/current.md` to no-active or open the next approved program.
