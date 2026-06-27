# PHASE06：架构图与 HTML 展示页

## 目标

把 Zuno 架构展示做成少图、清楚、稳定、可维护的展示层。

## 范围

- `docs/architecture/diagrams.md`
- `docs/architecture/overview.html`
- `.agent/architecture/blueprint.html`
- `tools/agent/render_architecture.py`

## 图谱范围

只维护三张核心图：

- Current Runtime
- Target Runtime
- Maintenance Workflow

## 风格

```text
背景：#f8f8fb
节点：#f6f3ff
边框：#a99cff
文字：#2c255f
线条：#9b8cff
节点少，箭头清楚，不做复杂 UML
```

## 不做

- 不维护十几张重复图。
- 不让 Markdown Mermaid 和 HTML Mermaid 变成两套真相。
- 不引入重前端站点。

## 验收

- GitHub Markdown 可直接渲染 Mermaid。
- HTML 页面能本地打开并显示三张图。
- Mermaid 源有单一维护来源或明确同步规则。
