# RB-WORKFLOW-V4-BOOTSTRAP

## 状态

```text
workflow: ZUNO-RED-BLUE-WORKFLOW-V4
status: READY_FOR_EXTERNAL_CHATGPT_REVIEW
round_006: READY_FOR_FRESH_RED_THREAD / NOT_STARTED
architecture_track: READY_FOR_FRESH_RED_THREAD
implementation_track: Wave-001 independent; WAITING_FOR_RED_COUNTER_RETEST
```

这是 V4 工作流契约的 Bootstrap Review Package，不是 Round-006，不包含 Red/Blue Session
身份，也没有启动任何 Thread。历史 Round-001 至 Round-005 保持 immutable。

## 读取顺序

1. [`review-package.md`](review-package.md)
2. [`manual-launch-instructions.md`](manual-launch-instructions.md)
3. [`../../05-red-blue/round-protocol-v4.md`](../../05-red-blue/round-protocol-v4.md)
4. [`../../05-red-blue/v4/`](../../05-red-blue/v4/)

机器校验：

```powershell
python tools/scripts/verify_red_blue_workflow_v4.py --bootstrap project-reconstruction-lab/sessions/RB-WORKFLOW-V4-BOOTSTRAP
```
