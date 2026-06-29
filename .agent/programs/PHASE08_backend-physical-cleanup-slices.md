# PHASE08：Backend Physical Cleanup Slices

> 状态：pending。目标是把 PHASE06 / PHASE07 的结论拆成可执行小切片。

## 目标

把 `src/backend/zuno` 的拥挤目录逐步变清楚，但每次只做一种低风险动作：

- 增加或修正目录 README。
- 建立 facade re-export。
- 迁移小型 contract / model / helper 文件。
- 删除已证明无引用的 legacy alias。
- 把 generated/local 产物纳入 ignore/verifier。

## 候选切片

| 切片 | 范围 | 目标 | 验证 |
| --- | --- | --- | --- |
| Slice A | `config/`、`settings.py`、`platform/` | 明确配置归属，避免 platform/config 双头叙事。 | settings / repo tests |
| Slice B | `schema/`、`api/` | 判断 DTO 是否逐步迁入 `api/dto`，或保留 `schema` 为 compatibility source。 | API contract tests |
| Slice C | `services/application/*` 到六层 facade | 优先迁移小型 capability/context/knowledge contracts。 | agent / retrieval focused tests |
| Slice D | `tools/`、`system_skills/` | 区分 runtime tools、local skills、system resources。 | tool tests / repo structure |
| Slice E | `legacy/`、retired aliases | 只删除有 grep 和 tests 证明的 legacy。 | legacy guard tests |

## 禁止

- 不一次性移动 `services/`。
- 不在一个切片里同时改 API、DB、GraphRAG 和 Agent runtime。
- 不为了视觉清爽牺牲 import compatibility。

## 完成标准

每个切片必须有：

- 变更文件列表。
- 旧路径和新路径。
- focused tests。
- rollback plan。
- docs / verifier 是否同步的判断。
