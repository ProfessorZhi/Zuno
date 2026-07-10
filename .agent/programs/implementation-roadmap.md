# Implementation Roadmap

state: active
active_program: zuno-lean-complete-product-architecture-v1
current_phase: PHASE02_lean-architecture-markdown
latest_completed_program: zuno-evidence-span-agentic-graphrag-hardening-v1

## Program Intent

把 Zuno 前台架构事实源收缩成一个可执行、可验证、短期可闭环的 Lean Complete Agentic GraphRAG Product 架构。

本轮不扩大 runtime 能力。它只修正文档、图、HTML、renderer、verifier 和 repo tests 的一致性，让后续实现工作有清楚的事实源。

收缩的是目标规模，不是文档精度。`docs/architecture/architecture.md` 必须保持详细的实施蓝图能力，能指导 owner、contract、配置、状态、失败、fallback、trace、测试、Program 和 Phase 拆分。

## 旧架构问题

- 十图结构来自 4+1 / View & Beyond 理论映射，读者难以直接判断产品怎么跑、用户怎么完成任务。
- 前台文档混有 11 层、四大交付物、历史 program、Production Scale 和短期目标，Current / Target / Future 边界过重。
- renderer、HTML、verifier 和 tests 把旧十图标题硬编码为当前事实，导致架构收缩无法只改 Markdown。
- Production Scale 内容太靠前，容易被误读为近期必须完成或已经完成。
- Agentic GraphRAG implementation available 与 fixed benchmark measured pass 的边界需要继续保持清楚。

## 新定位

Zuno 当前前台定位：

```text
Lean Complete Agentic GraphRAG Product
```

含义：

- 近期目标是一个本地优先、可演示、可评测、可继续硬化的企业知识库 Agentic GraphRAG 产品。
- 用户从聊天、知识库选择和模型配置进入，不手动拼 RAG / GraphRAG 工具链。
- Single Controller Agent 负责在一次任务中完成 context、planning、retrieval、tool use、citation、trace 和 response。
- fixed benchmark / release gate 仍是质量证明入口；没有 measured pass 就不能宣称 Agentic GraphRAG 质量完成。

## 六个 Runtime Domain

1. Product & API
2. Input & Knowledge
3. Agent Core
4. Capability & Tool
5. Governance & Observability
6. Local Infrastructure

每个 domain 必须按统一模板展开：定位、职责、不负责什么、代码 owner、核心 contract、runtime、输入、输出、配置、持久状态、失败与 fallback、安全边界、trace / metrics、focused tests、E2E 验收、当前状态、短期闭环项和 Future Optional。

## 必须保留的实施细节

- 代码 ownership matrix。
- 配置化和禁止写死契约。
- 核心持久对象和 restart recovery 边界。
- Agent run span tree、failure bucket、usage / cost / latency、citation diagnostics。
- Runtime 完成与质量完成的区别。
- Agentic GraphRAG baseline gate 和 measurement blocked 语义。

## 四张架构图

1. Lean System Overview
2. Golden Path Runtime
3. Agentic GraphRAG and Agent Loop
4. Local Deployment and State

## Phase Plan

### PHASE01_truth-source-and-product-positioning

- 打开 active program。
- 记录旧事实源问题、新定位、六域和四图目标。
- 不修改 runtime。

### PHASE02_lean-architecture-markdown

- 重写 `docs/architecture/architecture.md` 为详细实施蓝图事实源。
- 同步 README、architecture README、production readiness 和专题文档。
- 明确 Current / Target / Future Optional / History。

### PHASE03_four-diagram-html-and-guardrails

- 将 renderer、diagram inventory、verifier 和 docs entrypoint tests 改为四图契约。
- 运行 `python tools/agent/render_architecture.py --write` 生成 HTML 和 `.agent/architecture` 镜像。
- 检查 HTML 只有四张图、Mermaid 可渲染、全屏按钮存在。

### PHASE04_docs-sync-verification-and-closure

- 运行完整验证命令。
- 归档 program 到 `docs/history/programs/zuno-lean-complete-product-architecture-v1/`。
- `.agent/programs/` 回到 no-active。
- 提交并推送。
