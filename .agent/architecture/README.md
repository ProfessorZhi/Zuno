# Agent 架构工作区

`.agent/architecture/` 是 Agent 侧架构镜像，不是独立事实源。

## 同步规则

- `.agent/architecture/architecture.md` 必须与 `docs/architecture/architecture.md` 完全一致。
- `.agent/architecture/architecture.html` 必须与 `docs/architecture/architecture.html` 由同一个 Markdown 源生成。
- 修改架构图或总架构后运行：

```powershell
python tools/agent/render_architecture.py --write
python tools/agent/render_architecture.py --check
```

## 当前定位

Zuno 当前前台架构是 Lean Complete Agentic GraphRAG Product。

`architecture.md` 是详细实施蓝图；`architecture.html` 是十类视图和可展开子图的架构图谱。收缩的是近期目标规模，不是文档精度。

状态事实源见 `docs/architecture/production-readiness.md`。

## 禁止

- 不在 `.agent/architecture/` 写入独立结论。
- 不手写 HTML。
- 不恢复已归档 split architecture docs。
- 不把 Future Optional 写成 Current。
