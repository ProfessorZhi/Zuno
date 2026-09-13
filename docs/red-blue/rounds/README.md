# Red / Blue Rounds

本目录保存已经关闭的 `CHATGPT_AUTO` / `AGENT_AUTO` Round。Round 是面试模拟历史，不拥有 Project History、Target Architecture、Current Evidence 或真实 Resume Truth。

## 当前正式格式

Resume-first protocol 生效后的每轮固定为一个目录：

```text
<round-id>/
├── 00_manifest.yaml
├── 01_simulated_resume.md
├── 02_red_questions.md
├── 03_blue_answers.md
├── 04_red_evaluation.md
├── 05_blue_architecture_reflection.md
├── 06_workflow_retrospective.md
├── 07_user_feedback.md
└── 08_session_transcript.md
```

一轮对应一版固定 Zuno SHA 和一份冻结模拟简历。需要复测时创建新 Round，不在旧目录继续追加第二批问题。

各文件分别回答：

- `01`：当前文档能负责任地写出怎样的简历；
- `02`：真实面试官只看简历会怎么问；
- `03`：Zuno docs 能否支持候选人回答；
- `04`：面试官是否相信这些回答；
- `05`：暴露的是 Resume / Narrative / Architecture / Implementation / Evidence / Ownership / Fundamentals 中哪类问题；
- `06`：Red 的问题和整个 Harness 本身好不好；
- `07`：用户对本轮问题、回答、评价和工作流的直接反馈；
- `08`：CHATGPT_AUTO / AGENT_AUTO 的完整可观察过程。

Round 里的 Gap 只能触发独立修复任务。修改 Project / Architecture / Modules / Evidence / Resume / Red Skill 后，必须创建新 Round 复测。

## 旧格式 Round

本目录里已经存在若干旧协议 Round，它们继续原样保留，不为了新格式改写历史。

特别是：

`rb-2026-09-13-zuno-interview-batch-013`

采用了“Red 可以读取 Zuno 项目材料并据此出题”的旧方法。用户在后续 Review 中明确判定这种 Red 不合格：真实面试官应该只看到简历，而不是提前读完 Zuno Architecture / Evidence。该 Round 因而被标记为 **methodology superseded**，只能用于分析旧方法的问题，不能作为 resume-first Interview Red Team 的通过证据。

更早的 manual / early automated Round 继续留在 [`../archive/legacy/`](../archive/legacy/README.md)。