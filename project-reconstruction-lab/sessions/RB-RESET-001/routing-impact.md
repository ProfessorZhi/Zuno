# Routing Impact

## 已同步

- `AGENTS.md`：Red/Blue 指向 RESET 入口，不再把 V4.2 写成 active Protocol；
- `.agent/system.yaml`：保留历史验证触发范围，增加 reset/readability 路由说明；
- `.agent/references/current-program.md`、`.agent/programs/current.md`：关闭当前 Workflow
  Consolidation Program，Round-007 改为取消且未启动；
- `.agent/references/task-routing.md`、`verification-map.md`：先读 active reset 入口，历史协议
  仅按需考古；
- `project-reconstruction-lab/README.md`：把 Red/Blue 从当前执行入口改为历史/暂停路由；
- `docs/project/architecture/README.md`：增加可读性基线和下一轮前置门；
- `tools/scripts/verify_red_blue_reset.py` 与对应 repo test：验证本次边界。

## 明确未触碰

`project-reconstruction-lab/sessions/RB-WORKFLOW-V2-001` 至 `RB-WORKFLOW-V4.2-ROUND-006` 的
原始 Artifact、`docs/decisions/`、Facts、业务 Runtime、UI、Schema、Migration、Dependencies、
Production Infra 和历史分数/严重度/回答/Closure。
