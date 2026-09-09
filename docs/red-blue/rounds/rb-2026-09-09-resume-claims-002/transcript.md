# Transcript — rb-2026-09-09-resume-claims-002

Mode: `CHATGPT_AUTO`  
Retest of: `rb-2026-09-09-resume-claims-001`  
Zuno base: `3c5e3ed414a59c94fd90818f6b359a5ac75df4a5`  
Resume: `ProfessorZhi/internship-work@02fa954879dfdfb59f70b18ebd9d4b0e2b9b8033:resume/00_resume_versions/Zuno_v3+CodingAgent+SFTDPO_简历/Agent开发工程师／AI应用工程师+Zuno／CodingAgent／SFTDPO_事实对齐／可追问_简历草稿_v2.md`

本轮只复测上一轮三个 decision-changing 风险。测试条件保持同类岗位、同面试阶段和 `kernel-only` Red calibration，仅替换为已经合并的事实对齐候选简历。

## Turn 1 — Personal Ownership

### Red

新的 Zuno bullet 已经把很多“设计 / 实现”改成“参与”。继续追问：本人到底做了什么？如果只能说参与 Agent、Memory、Tool Calling，却讲不出一个明确需求、代码改动、Bug、测试和结果，这些 bullet 是否只是从夸大退回模糊？

### Blue

候选简历不再声称本人完整设计统一控制器、GraphRAG、三层 Memory、整个 Runtime 或评测系统。它明确写“参与部分 Agent 开发与 Tool Calling Strategy”“参与第一批 Memory 工作并接入 OpenViking”“通过 PostgreSQL 查看和调试实际项目数据”，并把 Architecture / Evidence 内容标为后续复盘。

这些表述与 Canonical Project / Provenance 当前能够确认的个人参与强度一致。但任务级 Evidence 仍不足：若面试官继续追一个具体需求、PR / commit、Bug、测试和结果，当前资料还不能稳定闭环。因此新的 Resume Truthfulness 风险已经解除，剩余问题是面试深挖证据不足。

### Source trace

- Candidate resume snapshot：Zuno 四条修订后 bullet。
- `docs/project/README.md`：部分 Agent、Memory、OpenViking、Tool Calling Strategy、数据库调试等方向级个人参与。
- `docs/governance/project-fact-provenance.md`：PF-009～PF-012 及所需任务级补证。

### Verifier

Verdict: `PARTIAL`  
Severity: `S2`  
Gap: `OWNERSHIP_GAP + EVIDENCE_GAP`  
Previous status: `S0 RESUME_CLAIM_RISK resolved`  
Next action: `NEXT_ATTACK_ANGLE`

## Turn 2 — Project Identity

### Red

候选简历改成“法律智能 Agent 平台”，并写 LIPLAB、天津法院智慧平台相关场景。这个身份是为修 Finding 临时增加的包装，还是项目事实？如果继续追问是否 22 家法院都在用、是否已经 Production，回答会不会再次扩大背景？

### Blue

Canonical Project 本身就把 Zuno 放在 LIPLAB 智慧司法研究与工程化、天津法院智慧平台相关场景中，因此新的项目身份不是临时创造。

同时 Project / Provenance 的上限也清楚：现有材料不足以证明全部 22 家法院正式部署或日常使用；可以确认法院侧测试与 Pilot Validation，但 Production、SLA 和全面部署没有建立。候选简历只写“面向天津法院智慧平台相关场景”，没有写 22 家全量部署或 Production。

### Source trace

- Candidate resume snapshot：`Zuno：法律智能 Agent 平台` 与项目简介。
- `docs/project/README.md`：智慧司法 / 天津法院相关背景与 Pilot / Production 边界。
- `docs/governance/project-fact-provenance.md`：PF-005、PF-018～PF-020。

### Verifier

Verdict: `PASS`  
Severity: `none`  
Previous status: `S0 PROJECT_REALITY_GAP / RESUME_CLAIM_RISK resolved`  
Next action: `NEXT_ATTACK_ANGLE`

## Turn 3 — Measurement wording

### Red

候选简历删除了“固定评测链路覆盖证据召回、完整证据链、无据拒答”，但仍写“复杂机制保留与否回到 Eval / ablation 证据”。当前到底有这些证据没有？这句话是否仍在暗示本人完成了对应评测？

### Blue

Current Evidence 仍明确是 `MEASUREMENT_BLOCKED`，没有正式质量 benchmark 或 GraphRAG ablation 结果，不能宣称这些收益已经被证明。

候选简历的句子描述的是后续架构复盘原则，并同时写明“将 Current 与 Target 分开”。它没有声称本人完成正式 ablation，也没有给出质量指标或收益数字。因此项目本身的 Measurement Gap 仍存在，但 Resume 不再把这个 Gap 包装成已完成个人成果。

### Source trace

- Candidate resume snapshot：`架构与证据复盘` bullet。
- `docs/evidence/current-eval-baseline.md`：`MEASUREMENT_BLOCKED`。
- `docs/evidence/current-test-baseline.md`：benchmark / quality / production readiness 的 Current 边界。

### Verifier

Verdict: `PASS`  
Severity: `none` for Resume wording  
Previous status: measurement-related `RESUME_CLAIM_RISK resolved`  
Known project state: `MEASUREMENT_GAP remains`  
Next action: `CLOSE_ROUND`

## Round close

三个原始 Resume 风险中，项目身份和 Measurement wording 已通过复测；个人 Ownership 的“强 Claim 真实性风险”也已解除。唯一仍会改变面试准备决策的缺口，是缺少能够把方向级参与升级成 3–5 分钟可追问个人故事的任务级 Evidence。
