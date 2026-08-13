# RB-WORKFLOW-V4.2-BOOTSTRAP

这是 V4.2 的 Workflow Contract Bootstrap，不是 Round-006 Operational Pilot。

本 Bootstrap 固定：

- `artifact_base_sha` 指向创建本契约时的 `main` 快照；
- `artifact_content_state: WORKFLOW_CONTRACT_AVAILABLE`；
- `round_006_status: READY_FOR_ADAPTIVE_RED_BLUE_PILOT`；
- `round_006_started: false`；
- `external_reviewed_sha: NOT_PROVIDED`。

它没有创建 Red / Blue Session，没有证明真实 Context Isolation，没有证明 Blue 未读取
Calibration，也没有执行 Main Merge。历史 V4.1 及更早 Round 保持 immutable。

验证：

```powershell
python tools/scripts/verify_red_blue_workflow_v42.py --bootstrap project-reconstruction-lab/sessions/RB-WORKFLOW-V4.2-BOOTSTRAP
```
