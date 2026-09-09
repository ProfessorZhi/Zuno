# Red / Blue Rounds

本目录保存新式 `CHATGPT_AUTO` / `AGENT_AUTO` Round 的长期结果。每个 Round 只记录当时固定的输入、实际问答与去重后的 Findings，不拥有 Project History、Target Architecture、Current Evidence 或 Resume Truth。

每个正式 Round 至少包含：

```text
<round-id>/
├── manifest.yaml
├── transcript.md
└── findings.md
```

`manifest.yaml` 固定 Zuno SHA、简历快照、岗位/阶段、模式、上下文范围和停止条件；`transcript.md` 保存实际 Red / Blue / Verifier 过程与 source trace；`findings.md` 保存真正会改变决策的去重结果。

Finding 只能触发独立修复任务。修改 Project / Architecture / Modules / Evidence / Resume 后，需要换措辞或换场景重新测试；Round 本身不会自动升级成新的 Canonical Truth。

旧手工与早期自动 Round 继续留在 [`../archive/legacy/`](../archive/legacy/README.md)。
