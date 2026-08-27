# Current Red / Blue Round

state: `no-active`
active_round: `none`
mode: `none`
resume_snapshot: `none`
target_role: `none`
interview_stage: `none`
red_calibration: `none`
blue_profile: `canonical-part-a-first`

`main` 默认必须保持 `no-active`。只有用户明确启动 Red / Blue 时，才创建临时 Round workspace 并把这里切到 active state；Round 结束后必须恢复 `no-active`，原始记录归档到 `docs/maintenance/history/red-blue/`。

## 允许的 active state

```text
state: `active-red-blue`
active_round: `<round-id>`
mode: `chatgpt-duel | autonomous-agent | human-candidate`
resume_snapshot: `<repo>@<sha>:<path>`
target_role: `<role>`
interview_stage: `<round/stage>`
red_calibration: `kernel-only | calibrated`
blue_profile: `canonical-part-a-first`
```

Round manifest 必须固定：Zuno base SHA、简历路径与 commit SHA、目标岗位、面试轮次、Red calibration sources、Blue allowlist。没有这些锚点时，不得把结果写成可比较的 Red/Blue Evidence。

当前：没有 active Round。