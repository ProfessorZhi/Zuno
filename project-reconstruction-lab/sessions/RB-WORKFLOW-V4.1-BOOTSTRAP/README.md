# RB-WORKFLOW-V4.1-BOOTSTRAP

这是 V4.1 工作流的 Bootstrap Review Package，不是 Round-006。它没有创建 Red/Blue Session，
没有生成 Questions，也没有修改 Canonical Architecture。

```text
workflow: ZUNO-RED-BLUE-WORKFLOW-V4.1
architecture_track: ROUND-006 READY_FOR_FRESH_RED_THREAD / NOT_STARTED
implementation_track: Wave-001 independent / WAITING_FOR_RED_COUNTER_RETEST
status: READY_FOR_EXTERNAL_CHATGPT_REVIEW
```

入口：

- [`review-package.md`](review-package.md)
- [`manual-launch-instructions.md`](manual-launch-instructions.md)
- [`../../05-red-blue/round-protocol-v4.1.md`](../../05-red-blue/round-protocol-v4.1.md)
- [`../../05-red-blue/v4.1/`](../../05-red-blue/v4.1/)

V4.1 Addendum 的提问校准模板是 [`../../05-red-blue/v4.1/interview-calibration-packet.md`](../../05-red-blue/v4.1/interview-calibration-packet.md)。它只提供给 Red Thread，
只包含提问行为模式，不包含候选人答案、项目包装或 Zuno 事实；Blue Thread 明确禁止读取。

```powershell
python tools/scripts/verify_red_blue_workflow_v41.py --bootstrap project-reconstruction-lab/sessions/RB-WORKFLOW-V4.1-BOOTSTRAP
```
