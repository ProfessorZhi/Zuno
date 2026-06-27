# PHASE02：本地 Agent Skill System 收口

## 目标

把 `.agent` 明确定义为 Zuno Local Agent Skill System，而不是普通索引目录。

## 范围

- `AGENTS.md`
- `.agent/README.md`
- `.agent/system.yaml`
- `.agent/references/`
- `.agent/templates/`
- `.agent/programs/`

## 目标结构

```text
AGENTS.md = bootloader
.agent/architecture = 长期设计
.agent/programs = 当前执行计划
.agent/references = 本地项目 skills / lessons / playbooks
.agent/templates = skill 执行模板
tools/agent + tools/verify = 自动化脚本目标位置
tests/agent_system = 工作流防回归目标位置
docs = 人类正式真相
```

## Skill 文件标准

`.agent/references/*.md` 如果承载本地 skill，必须回答：

- When To Use
- Mental Model
- Current Truth
- Target Direction
- Must Preserve
- Before Editing
- Allowed Changes
- Forbidden Changes
- Common Failure Patterns
- Debug Playbooks
- Focused Tests
- Docs Sync
- Lessons Learned

## 不做

- 不把一次性调查流水账写进 references。
- 不新建 `.agent/skills/` 或 `.agent/workflows/`。
- 不把 scripts 继续塞进 `.agent` 作为长期目标；现有 `.agent/scripts` 只保留到 PHASE03 迁移或明确保留。

## 验收

- `AGENTS.md` 明确 `.agent` 是本地 Skill System。
- `.agent/system.yaml` 能把路径路由到 skills、templates 和 verify 命令。
- `.agent/references/README.md` 不再把 references 定义为普通索引。
- `.agent/templates/README.md` 说明模板只存执行骨架，不存项目知识。
