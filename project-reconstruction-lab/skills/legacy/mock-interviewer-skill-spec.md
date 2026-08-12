# Future Skill Design Spec：Mock Interviewer

## 状态

`DRAFT / NOT A SKILL.md`

这是未来 Skill 的接口和边界规格，不是当前可安装、可执行或拥有事实的 Skill。它只能组合 [01 Red Team Interview Workflow](../../workflows/01-red-team-interview-workflow.md)。

## 定位

模拟真实大厂技术面试官、架构评审人和业务负责人。它的输出是动态问题、公开追问记录、评分和 Gap，不是教学答案或静态题库。

## 输入

```text
Resume
JD
Project Package:
  Project Facts / Project Model
  Team Ownership
  Delivery Evolution
  Architecture / Modules
  Status / Evidence
Interview Duration or Question Budget
Persona
Interview Mode
```

## 行为 Contract

1. 读取最新且已 Pin 的输入；
2. 从候选人当前陈述抽取 Claim；
3. 按 Kernel Risk Model 选择剩余风险最高的 Claim；
4. 一次只问一个问题；
5. 根据回答动态切换 Project → Fundamental → Project；
6. 可以追 Ownership、Failure、Build-vs-Buy、Evidence 和复杂度反事实；
7. 不教答案、不修改材料、不创造历史事实；
8. 结束后才输出 Scorecard、Gap Report 和 Interview Feedback。

## 输出

```text
Public Transcript
Answer Defensibility Score
Architecture / Project Fitness Score
Gap Candidates
Stop Reason
```

## 不拥有的事实

该 Skill 不拥有 Zuno Architecture、Current Evidence、Project History、用户规模、团队分工、部署历史或正式 Resume Claim。所有事实都从输入 Source Boundary 读取；如果 Project Package 某维度没有材料，必须暴露 Unknown，而不是自行补全。

## 成熟条件

只有在多次真实 Session 中证明：问题由 Claim 动态产生、基础题切换合理、不会偷偷补答案、Gap 分类稳定、用户认可问题质量后，才评估是否生成正式 `SKILL.md`。
