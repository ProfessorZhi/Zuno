# Current Red / Blue Round

state: `no-active`
active_round: `none`
mode: `none`
resume_snapshot: `none`
target_role: `none`
interview_stage: `none`
red_calibration: `none`
blue_profile: `canonical-part-a-first`

`main` 默认保持 `no-active`。只有明确启动 Red / Blue 时才创建临时 Round workspace；Round 结束后恢复 `no-active`，长期结果归档到 `docs/red-blue/rounds/<round-id>/`。

## 允许的 active state

```text
state: `active-red-blue`
active_round: `<round-id>`
mode: `CHATGPT_AUTO | AGENT_AUTO`
resume_snapshot: `<repo>@<sha>:<path>`
target_role: `<role>`
interview_stage: `<round/stage>`
red_calibration: `kernel-only | calibrated`
blue_profile: `canonical-part-a-first`
```

只有上面两种自动执行模式属于正式 contract。用户可以中途 intervention，但 intervention 不改变 `mode`。

Round manifest 必须固定 Zuno base SHA、精确简历 snapshot、目标岗位/面试阶段、scenario scope、Red calibration policy、Blue allowlist 和停止条件。缺少这些锚点时，Round 只能作为临时讨论，不进入正式归档。

当前：没有 active Round。