# PHASE03：tools / tests 工作流防回归

## 目标

把本地 Agent 工作流从“靠文档约定”推进到“有 tools 和 tests 防漂移”。

## 范围

- `tools/agent/`
- `tools/verify/`
- `tests/agent_system/`
- 现有 `.agent/scripts/` verifier 的迁移或保留决策
- repo structure / docs boundary verifier

## 目标能力

- `verify_programs_flat`：检查 `.agent/programs` 只存当前平铺计划，新计划必须从 `PHASE01` 开始。
- `verify_skill_files`：检查 `.agent/references` skill 文件结构。
- `verify_docs_drift`：检查 README、docs、AGENTS、`.agent/current` 不互相漂移。
- `verify_system_yaml`：检查 `.agent/system.yaml` 路由文件引用存在。

## 不做

- 不改 runtime 行为。
- 不把验证器做成复杂框架。
- 不引入新依赖。

## 验收

- repo tests 覆盖 `PHASE01` 编号规则。
- verifier 不再硬编码旧 active Phase 05-09。
- 旧 `.agent/scripts` 若仍保留，必须有明确过渡说明。
