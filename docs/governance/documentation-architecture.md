# Zuno Documentation Architecture Reference

status: canonical-documentation-architecture
owner: Documentation Governance Owner

## 1. Physical layout

`docs/` uses eight top-level directories because eight long-lived responsibilities need distinct navigation. Physical layout does not imply equal truth authority.

```text
System & Review
project/        project history, context, team/personal participation
architecture/   accepted Target cross-cutting architecture
modules/        accepted Target responsibility decomposition
red-blue/       interview/adversarial review method, active workspace and archived rounds

Trust & Evolution
research/       upstream research, algorithms, court/project background, platform baselines
decisions/      accepted architectural rationale
evidence/       Current code/test/trace/eval/runtime evidence
governance/     provenance, ownership, documentation rules, routing, workflow, operations
```

There is no `maintenance/` top-level domain. Agent/GitHub workflow and operational runbooks are governance responsibilities. Red / Blue has its own top-level review domain because it has an independent lifecycle, source policy, active workspace and archive, while remaining non-authoritative for Project, Architecture and Current Evidence.

Within `red-blue/`:

```text
README.md       human method
workspace/      active resume-first round workspace
rounds/         closed round archive
archive/legacy/ retired manual / earlier automated methods
```

## 2. Truth ownership

```yaml
history:
  owner: docs/project/
target_cross_cutting_architecture:
  owner: docs/architecture/
target_responsibility_decomposition:
  owner: docs/modules/
accepted_design_rationale:
  owner: docs/decisions/
current_evidence:
  owner: docs/evidence/
rules_and_provenance:
  owner: docs/governance/
upstream_research:
  owner: docs/research/
  authority_limit: cannot_raise_target_or_current
adversarial_review:
  owner: docs/red-blue/
  authority_limit: findings_require_independent_acceptance
```

Research and Red / Blue are canonical locations for their own artifacts but are not additional owners of system truth. A paper, external platform feature, Red concern, Blue proposal, simulated resume or archived Round cannot modify Target or Current by existing in the repository.

## 3. Human / Machine projection

Project、Architecture 和 Module 都区分 Human Narrative 与 Engineering Reference，但总体架构额外保留一个显式的正文文件名：

```text
project/README.md                    Human Narrative
project/reference.md                 Project fact / ownership reference

architecture/README.md               directory entry only
architecture/architecture.md         Overall Target Architecture Human Narrative
architecture/reference.md            Architecture Engineering / Agent Reference

modules/README.md                    Human responsibility map
modules/reference.md                 Cross-module Engineering Reference
modules/<semantic-name>/README.md    Module Human Narrative
modules/<semantic-name>/reference.md Module Engineering Reference
```

`architecture/README.md` 只负责把读者送到 `architecture.md`、`reference.md`、views 和 rendered output；它不复制 Target Architecture。显式的 `architecture.md` 让总体架构在文件系统里拥有清楚、可引用的 Canonical Human 文档，同时保留 GitHub 目录默认 README 的导航体验。

Project reference 是历史事实与 Ownership 的机器索引。Architecture reference 保存跨模块 Part B。每个 Module reference 保存该责任域的 Part B、Detail Candidate 与 Part C Cross-Module Consistency。

Human-facing narrative 建立 mental model，优先保存 scenario、baseline、failure、causality、normal flow、failure/recovery、alternative、trade-off 和 simplification condition。内部对象名应在概念已经被解释以后出现。

Engineering reference 压缩已经接受的语义：Owner、Authority、Contract、Version、Completion Proof、Idempotency、Persistence、Retry/Replan/Reconcile、Security、Failure Matrix、Detail Candidate 和 Source Map。

Human Narrative 与 Engineering reference 共享同一 Truth Owner。物理拆分不能产生两套 Architecture、Module 或 Current 事实。Human prose 可以改变叙事结构，Engineering reference 可以提高检索密度；两者都不得静默改变 Architecture Owner、Authority、Contract semantics、Recovery semantics、Security Authority、Current/Target level、Evidence status 或 Personal Ownership。

## 4. Default reading paths

Human default:

```text
docs/README.md
→ project/README.md
→ architecture/architecture.md
→ modules/README.md
→ selected modules/<semantic-name>/README.md
→ evidence/README.md
```

Research is pulled in only when a claim needs its lineage or an external baseline. Red / Blue is intentionally excluded from first reading: the book must stand on its own before interview/adversarial review begins.

Agent implementation default:

```text
architecture/reference.md
→ modules/reference.md
→ selected modules/<semantic-name>/reference.md
→ relevant neighboring module reference.md
→ decisions/
→ evidence/
→ code/test/schema/migration
```

When implementation reasoning loses causality, the agent returns from `architecture/reference.md` to `architecture/architecture.md`, or from a Module reference to that Module README. It does not infer fields or Current status from the narrative. Project-fact or resume-ownership work additionally reads Project reference and Governance provenance.

## 5. Module decomposition

Documentation Architecture does not freeze module count. Current numbering reflects the accepted Target decomposition at this point in architecture history. Merge/split requires an Architecture Revision or accepted ADR with migration impact and semantic-alignment review.

A logical responsibility boundary is not automatically a Python package, worker, process, container or network service.

## 6. Research boundary

`research/` stores evidence and reasoning inputs such as LIPLAB/Jidong Ge research lineage, legal capability algorithms, court-project background, and current generic-agent-platform baselines.

The trace should be recoverable as:

```text
Research Problem
→ Research Artifact
→ input/output/scope/evaluation
→ Engineering Gap
→ stable Capability semantics or architecture concern
→ Target responsibility
→ Current/Target/Unknown
→ Evidence
```

Missing links stay `UNVERIFIED`. Research cannot manufacture implementation status, production readiness, personal ownership or a requirement that does not exist in the business scenario.

## 7. Red / Blue boundary

Red / Blue is a resume-first interview review system, not an architecture author and not a repository-aware Red reviewer.

The normal sequence is:

```text
current Project / Architecture / Modules / Evidence
→ Resume Builder synthesizes one interview-grade simulated resume
→ simulated resume is frozen
→ Red sees only resume + JD + Red Interview Skill + general knowledge
→ Blue answers Red questions from accepted Zuno docs / Evidence
→ Red evaluates the answers without reading Zuno docs
→ Blue reflects whether weaknesses are Resume / Narrative / Docs / Architecture / Implementation / Evidence / Ownership / Fundamentals
→ Workflow Retrospective audits Red question quality and the Harness itself
→ user feedback is preserved
→ Round closes
→ any accepted repair happens in an independent task
→ a new Round generates a new simulated resume and retests
```

Formal execution modes are only:

```text
CHATGPT_AUTO
AGENT_AUTO
```

A user may interrupt either mode, but human participation is not a third execution mode.

### Resume Builder is the only pre-Red bridge to Zuno docs

The Builder may read current canonical docs, Current Evidence, provenance and a prior resume style. Its output is `01_simulated_resume.md`, which represents what the current documentation can responsibly claim in an interview artifact.

The simulated resume is not a new Truth Owner and does not automatically replace the user's real resume.

### Red source boundary

After the simulated resume is frozen, Red must not read:

```text
docs/project/
docs/architecture/
docs/modules/
docs/evidence/
docs/decisions/
docs/governance/
Zuno source / PR / commit diff
Blue source trace
```

Red instead uses the simulated resume, job/JD, the distilled Red Interview Skill and general technical knowledge. This prevents answer-aware question generation.

The Red Skill may be improved from user interviews and public interview corpora in a separate maintenance task. Raw interview corpora are not the default context for each Round.

### Blue source boundary

Blue receives the frozen simulated resume, Red questions and an explicit Zuno canonical-doc allowlist. It may concede Unknown or Target-only facts; it must not use external interview material to invent Zuno history.

### Red Evaluation and Blue Reflection remain distinct

Red Evaluation asks whether a real interviewer would believe and accept the answers. It still does not read Zuno docs.

Blue Architecture Reflection then uses the docs to determine whether the interview weakness actually warrants a Resume change, Narrative change, evidence recovery, implementation work, architecture revision, fundamental-study task, or no Zuno change.

### Workflow Retrospective audits the attacker

A formal Round must evaluate Red itself. It checks resume grounding, technical depth, full-chain coverage, non-duplication, Build/Buy skepticism, failure pressure, fundamentals drilldown, interviewer realism, information gain and user alignment.

User feedback about Red quality has priority over self-reported PASS rates. If the user says the questions are low-value, Reviewer-like or repetitive, the workflow must investigate the Red Skill / context firewall / question budget rather than treating the Round as successful because Blue answered many questions.

### Active workspace and archive

Active Round:

```text
docs/red-blue/workspace/<round-id>/
```

Closed Round:

```text
docs/red-blue/rounds/<round-id>/
```

Each resume-first Round preserves the same nine artifacts from simulated resume through workflow retrospective, user feedback and session transcript. CHATGPT_AUTO and AGENT_AUTO share this archive contract.

A Round produces one Red question batch, default 100 questions. Retest creates a new Round rather than mixing multiple documentation/resume versions in the same folder.

Red / Blue outputs are non-authoritative. High-severity findings require independent source review, implementation evidence or accepted architecture/documentation changes before they affect canonical owners.

## 8. Architecture reasoning contract

Important Target decisions should preserve a recoverable chain:

```text
stakeholder / business concern
→ concrete scenario and failure consequence
→ simplest viable baseline
→ constraint exposed by the scenario
→ candidate tactic / boundary / reuse option
→ considered alternative
→ chosen direction
→ trade-off and new failure surface
→ measurement / evidence needed
→ revisit, merge or deletion condition
```

This is not a Markdown template. It is a test for whether the architecture can be explained causally without relying on internal nouns.

Scenario-driven review can borrow the intent of QAW/ATAM: discover quality-driving scenarios early, then use a mature design to identify sensitivity points, trade-offs and risks. Zuno does not require formal QAW or ATAM ceremonies.

A useful review trace is:

```text
prioritized scenario
→ architectural response
→ sensitivity point
→ competing authority / quality concern
→ risk or trade-off
→ evidence needed
→ accept, revise, simplify or defer
```

Single Controller, independent services, GraphRAG, Reflection, persistent Multi-Agent or Native Runtime remain examples of measurement-gated choices. Existing implementation does not grant permanence.

## 9. Governance-owned operational material

Cross-document terminology lives at `docs/governance/terminology.md`.

Human Agent/GitHub workflow lives under `docs/governance/workflows/`.

Operational migration and recovery runbooks live under `docs/governance/operations/`. A runbook can describe how to operate a mechanism; its existence does not prove Production Readiness.

## 10. Migration rule

Physical moves must not create duplicate truth. During migration, update repository navigation, `.agent` routing, validators and internal links in the same PR. Old compatibility paths should be removed once all supported routes are updated instead of being kept indefinitely as parallel entrypoints.

The Architecture directory entry / `architecture.md` / `reference.md` split and each Module README/reference split must preserve semantic equivalence across the boundary: Architecture Human Narrative remains in `architecture.md`; Module Part A remains human-facing in Module README; Part B/C remain engineering-facing; and no Owner/Authority/Recovery/Current-Target rule may disappear merely because it moved files.