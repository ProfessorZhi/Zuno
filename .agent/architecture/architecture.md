# Zuno Target Architecture Atlas — Agent Entry

status: generated-entrypoint  
normative_source: `docs/architecture/architecture.md`  
visual_atlas: `docs/architecture/architecture.html`

本文件不再复制完整架构正文，避免两份大型 Mermaid 图谱产生内容漂移。

Agent、Codex 和自动化工具在进行架构审阅、实现计划或代码修改前，必须读取：

1. `docs/architecture/architecture.md`：目标架构唯一规范事实源；
2. `docs/architecture/architecture.html`：4+1、Views & Beyond 与 Zuno Product Core 的十类 Mermaid 图谱；
3. `docs/architecture/production-readiness.md`：当前真实实现、差距和测量状态。

更新流程：

```powershell
python tools/agent/render_architecture.py --write
python tools/agent/render_architecture.py --check
python tools/scripts/verify_docs_entrypoints.py
```

边界：

```text
architecture.md = Target
production-readiness.md = Current
implementation available / measurement blocked / quality not yet proven
```
