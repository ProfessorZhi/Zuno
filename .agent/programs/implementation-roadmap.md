# Program Roadmap

state: no-active
active_program: none
current_phase: none
latest_completed_program: zuno-evidence-span-agentic-graphrag-hardening-v1

## 当前路线状态

当前没有 active program。最近完成的 roadmap 已归档：

- `docs/history/programs/zuno-evidence-span-agentic-graphrag-hardening-v1/implementation-roadmap.md`

## 后续 Target

- 修复或拆分 agentic profile runner，使 EnterpriseRAG paired eval 能完整产出 measured `agentic_graphrag` profile。
- 重新运行 release gate，并只在 fixed benchmark 完整产出后判断质量闸门。
- 如果 gate 失败，按 failure bucket 定位：retrieval、evidence text、citation binding 或 answer synthesis。

## 开新 program 规则

- 新 program 必须从 `PHASE01` 开始。
- 旧 phase 文件必须保留在 `docs/history/programs/`，不得复制回前台冒充 active。
- 每个 phase 的 Current 必须来自代码、测试、trace/eval 或 verifier。
