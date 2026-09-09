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
red-blue/       adversarial review method and archived review rounds

Trust & Evolution
research/       upstream research, algorithms, court/project background, platform baselines
decisions/      accepted architectural rationale
evidence/       Current code/test/trace/eval/runtime evidence
governance/     provenance, ownership, documentation rules, routing, workflow, operations
```

There is no `maintenance/` top-level domain. Agent/GitHub workflow and operational runbooks are governance responsibilities. Red / Blue has its own top-level review domain because it has an independent lifecycle, source policy and archive, while remaining non-authoritative for Project, Architecture and Current Evidence.

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

Research and Red / Blue are canonical locations for their own artifacts but are not additional owners of system truth. A paper, external platform feature, Red concern, Blue proposal or archived Round cannot modify Target or Current by existing in the repository.

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

Research is pulled in only when a claim needs its lineage or an external baseline. Red / Blue is intentionally excluded from first reading: the book must stand on its own before adversarial review begins.

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

Red / Blue is a review system, not an architecture author.

The normal sequence is:

```text
Human Narrative reaches independent readable quality
→ Red attacks concrete business scenarios, substitutes and failure windows
→ Blue answers closed-book from accepted Human Narrative/reference/Evidence or concedes a gap
→ Round produces findings
→ findings are classified
→ independent Writing / Architecture / Evidence / Ownership / Simplification work
→ accepted change enters the corresponding owner
→ retest with different wording/scenario
```

Formal execution modes are only:

```text
CHATGPT_AUTO
AGENT_AUTO
```

A user may interrupt either mode, but human participation is not a third execution mode.

Red should maximize information gain, not question count. A useful attack connects a stakeholder goal to a concrete stimulus, environment, expected response, unacceptable consequence, current design response, substitute and evidence requirement. It should prefer business failures such as stale evidence, provider mismatch, late results, ambiguous external effects, authorization changes, cost/complexity or unsupported ownership claims over internal terminology trivia.

Blue protects the project goal, not the current architecture. It may conclude that a generic platform is sufficient, a mechanism should be deleted, an Architecture Revision is needed, or available evidence is insufficient.

LLM agreement is not evidence. Because Red and Blue may share model biases, high-severity findings require source traceability and, for formal acceptance, independent evidence or an isolated `AGENT_AUTO` retest where appropriate.

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