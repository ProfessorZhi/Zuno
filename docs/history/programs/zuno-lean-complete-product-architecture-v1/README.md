# zuno-lean-complete-product-architecture-v1

status: completed
completed_on: 2026-07-10

## Program 目标

将 Zuno 的前台目标架构从过重的企业平台蓝图，收缩为 Lean Complete Agentic GraphRAG Product。

本轮收缩的是近期目标规模，不是架构文档精度。`docs/architecture/architecture.md` 仍是详细、规范、可实施的目标架构事实源；`docs/architecture/architecture.html` 是四张核心图的展示摘要。

## Phase

1. PHASE01_truth-source-and-product-positioning
2. PHASE02_lean-architecture-markdown
3. PHASE03_four-diagram-html-and-guardrails
4. PHASE04_docs-sync-verification-and-closure

## 完成边界

- 项目定位改为 Lean Complete Agentic GraphRAG Product。
- 六个运行域成为前台主架构边界。
- 黄金端到端链路成为短期主叙事。
- HTML 从旧十图收缩为四张图。
- renderer、verifier、docs entrypoint tests 和 diagram inventory 同步为四图契约。
- Production Scale 内容降为 Future Optional。
- 短期 closure gap 固定为 P0 / P1 / P2。

## 非完成声明

本轮只收缩和重写目标架构，没有声称运行质量已经提升。

Agentic GraphRAG 是否真正完成，仍以 fixed benchmark 和 release gate 为准。
