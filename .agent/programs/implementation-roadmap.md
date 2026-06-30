# Zuno Architecture Detail And Execution Plan Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 先细化 Zuno 目标架构文档、十类 Mermaid 架构图和生成 HTML，再从图反推出 Memory Layer、企业知识库、文档解析、安全和评测的后续执行计划。

**Architecture:** 本 program 不改 runtime。它把 `Model / Agent Core Runtime / Memory / Tool / Knowledge / Document Ingestion / Security / Trace-Eval / Platform` 写进 Target 架构，并保持 Current / Target / Future / History 边界。Memory Layer 明确为 Raw Event Log、Recent Window、Task Summary、Structured Long-term Memory、Context Pack、PostTurn Pipeline、review / promotion / decay 的 write-manage-read 子系统。十类图仍保持十个 canonical title，但每张图展开到二级组件。

**Tech Stack:** Markdown、Mermaid、`tools/agent/render_architecture.py`、Zuno `.agent/programs` 生命周期、repo verifiers、pytest repo tests。

---

state: active
program: zuno-architecture-detail-and-execution-plan-v1
current_phase: PHASE01_architecture-state-and-program-boot

每次新 program 都从 `PHASE01` 开始编号。

最近完成归档仍是 `zuno-eight-deliverables-full-realization-v1`，归档路径是 `docs/history/programs/zuno-eight-deliverables-full-realization-v1/`。

## 文件结构

- 修改 `docs/architecture/target-architecture.md`：正式 Target 分层、Agent Core Runtime、Memory Layer、Document Ingestion、ToolCard adapter、安全和 LangSmith eval 边界。
- 修改 `docs/architecture.md`：十类 Mermaid 图的唯一源，所有图保持 canonical title。
- 生成 `docs/architecture.html`：由 renderer 输出，不手写。
- 修改 `.agent/references/diagram-inventory.md`：登记十类图的二级组件要求和更新触发条件。
- 修改 `.agent/programs/*`：打开 active program、写 roadmap、phase 和 closure checklist。
- 修改 `.agent/references/current-program.md`、`docs/architecture/roadmap.md`、`README.md`、`.agent/architecture/future/programs/README.md`：同步当前 active program。
- 修改 `AGENTS.md`、`docs/architecture/README.md`：同步架构治理入口和图细化规则。
- 修改 `tools/agent/render_architecture.py`：放宽图展示宽度以容纳二级组件图。
- 修改 `.agent/scripts/verify_agent_system.py`、`.agent/scripts/verify_doc_boundaries.py`、`.agent/scripts/verify-workflow.ps1`、`tools/scripts/verify_docs_entrypoints.py`、`tools/scripts/verify_repo_structure.py`、`tests/repo/test_agent_system.py`、`tests/repo/test_docs_entrypoints.py`：让 verifier/test 固定 active program 与细化图契约。

### Task 1: Program Boot And State Surfaces

**Files:**
- Modify: `.agent/programs/current.md`
- Modify: `.agent/programs/README.md`
- Modify: `.agent/references/current-program.md`
- Modify: `docs/architecture/roadmap.md`
- Modify: `README.md`
- Modify: `AGENTS.md`
- Modify: `.agent/architecture/future/programs/README.md`
- Create: `.agent/programs/PHASE01_architecture-state-and-program-boot.md`

- [ ] **Step 1: Confirm git branch and clean scope**

Run:

```powershell
git status --short --branch
```

Expected: branch is `codex/zuno-architecture-detail-plan-v1` and unrelated files are not dirty.

- [ ] **Step 2: Open the active program**

Update active state files to include:

```text
program: zuno-architecture-detail-and-execution-plan-v1
state: active
current_phase: PHASE01_architecture-state-and-program-boot
```

- [ ] **Step 3: Keep completed program evidence visible**

Keep these phrases in state surfaces:

```text
zuno-eight-deliverables-full-realization-v1
docs/history/programs/zuno-eight-deliverables-full-realization-v1/
Codex 执行协作
不是 Zuno runtime 架构
不是多线程模式
```

### Task 2: Target Architecture Detailing

**Files:**
- Modify: `docs/architecture/target-architecture.md`

- [ ] **Step 1: Add target architecture detail layers**

Add the target table for:

```text
Model / Gateway
Agent Core Runtime
Context / Memory
Capability / Tool
Knowledge / Retrieval
Document Ingestion
Security / Policy
Trace / Eval
Platform / Workspace
```

Memory Layer 必须展开为：

```text
Raw Event Log
L0 Working Context
L1 Recent Window
L2 Task Summary
L3 Structured Long-term Memory
L4 Graph Memory
read path
write path
review / promotion / decay
memory eval
```

- [ ] **Step 2: Define Planning and Runtime boundary**

Document this contract:

```text
Planning is an Agent Core Runtime control capability.
LangGraph is a target implementation candidate for planning runtime orchestration.
LangGraph is not the planning module itself.
```

- [ ] **Step 3: Define ToolCard execution adapter boundary**

Document `execution mode` values:

```text
local_function | local_sdk | sdk_to_api | api | local_cli | cli_to_api | ssh | mcp_local | mcp_remote
```

### Task 3: Mermaid And HTML Detail Refresh

**Files:**
- Modify: `docs/architecture.md`
- Modify: `.agent/references/diagram-inventory.md`
- Modify: `tools/agent/render_architecture.py`
- Generate: `docs/architecture.html`

- [ ] **Step 1: Keep exactly ten canonical diagrams**

Do not add an eleventh Mermaid block. Keep:

```text
Logical View
Development View
Process View
Physical View
Scenarios View
V&B Logical View
Component-and-Connector View
V&B Deployment View
Quality View
Agent Loop View
```

- [ ] **Step 2: Expand each diagram to second-level components**

Each diagram must show at least one of:

```text
Agent Core Runtime
Document Ingestion
Security / Policy
Trace / Eval
Tool execution adapter
Knowledge / GraphRAG
```

- [ ] **Step 3: Generate HTML**

Run:

```powershell
python tools/agent/render_architecture.py --write
python tools/agent/render_architecture.py --check
```

Expected: both commands pass.

### Task 4: Execution Roadmap From Architecture

**Files:**
- Modify: `.agent/programs/implementation-roadmap.md`
- Modify: `docs/architecture/roadmap.md`
- Modify: `README.md`

- [ ] **Step 1: Derive follow-up implementation order**

Record this dependency order:

```text
architecture detail
-> Memory Layer write-manage-read contract
-> Document Ingestion / Parse Gateway
-> Enterprise Knowledge Base scenario
-> Security / Policy gates
-> LangSmith trace and eval
-> frontend trace / artifact product loop
```

- [ ] **Step 2: Preserve Current / Target boundary**

Do not move Document Ingestion, LangSmith, security gates or frontend trace into Current until code and tests prove them.

### Task 5: Validation And Closure

**Files:**
- Modify: `.agent/scripts/verify_agent_system.py`
- Modify: `.agent/scripts/verify_doc_boundaries.py`
- Modify: `.agent/scripts/verify-workflow.ps1`
- Modify: `tools/scripts/verify_docs_entrypoints.py`
- Modify: `tools/scripts/verify_repo_structure.py`
- Modify: `tests/repo/test_agent_system.py`
- Modify: `tests/repo/test_docs_entrypoints.py`
- Modify: `.agent/programs/closure-checklist.md`

- [ ] **Step 1: Update verifiers for active program**

Verifier must accept:

```text
state: active
zuno-architecture-detail-and-execution-plan-v1
PHASE01_architecture-state-and-program-boot.md
PHASE05_validation-and-closure.md
```

- [ ] **Step 2: Run validation**

Run:

```powershell
git diff --check
python tools/agent/render_architecture.py --check
python .agent/scripts/verify_agent_system.py
python .agent/scripts/verify_doc_boundaries.py
python .agent/scripts/verify_repo_hygiene.py
python tools/scripts/verify_docs_entrypoints.py
python tools/scripts/verify_repo_structure.py
powershell -NoProfile -ExecutionPolicy Bypass -File .agent/scripts/verify-workflow.ps1
pytest -q tests/repo/test_docs_entrypoints.py tests/repo/test_repo_structure_consistency.py tests/repo/test_agent_system.py -p no:cacheprovider
```

Expected: all pass.

- [ ] **Step 3: Commit and push**

Run:

```powershell
git add .
git commit -m "docs: detail zuno architecture program"
git push -u origin codex/zuno-architecture-detail-plan-v1
```
