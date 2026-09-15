# Session Transcript — rb-2026-09-15-formal-019

## 2026-09-15 — Round initialization

- Controller re-read current repository state and found no active formal round.
- Archived PR #236 / round #018 was confirmed as `INVALID_WORKFLOW_CALIBRATION`; its interview verdict, architecture findings and improvement ledger were excluded as formal inputs.
- Before starting the new round, Red Skill was calibrated from the user's first-party Shopee / 水滴集团 / 杭州泛讯 interview records.
- Added four explicit Red behaviors before pinning the round: `Subtraction Test`, `Ownership Interrupt`, `Evidence Escalation`, and `Project → Fundamental Bridge`.
- Formal round base fixed at `main@a8b0e540d9c138071ba671733e88a4142bd77a60`.
- Branch created: `red-blue/rb-2026-09-15-formal-019`.
- Execution mode: `CHATGPT_AUTO + BATCH_DUEL`.
- Resume was regenerated from canonical Zuno truth rather than copied from invalid #018.
- An internal fact-boundary appendix was initially appended to `01_simulated_resume.md`, then immediately removed before the Resume Gate because Red reads the whole frozen resume and must not receive hidden source hints.

## Resume Builder source boundaries

The generated resume is constrained by current canonical provenance:

- user joined after the project already existed; no founder/from-scratch claim;
- Tool/MCP historical personal work is bounded to the 2026-04 concrete Tool binding/config-injection and Workspace routing/hardening slices;
- later Tool Control Plane / PreparedAction / Approval / Idempotency / EffectReceipt / Reconcile cannot be backported into the historical resume;
- GraphRAG result is a five-query HotpotQA development smoke supporting a regression-fix story, not a formal benchmark or general superiority claim;
- Context/Memory V2 claims are bounded to typed contracts, scoped read/write/orchestration and readback hardening; no claim of owning the entire Memory architecture;
- project status is Internal Demo / court-side testing / Pilot Validation, not Production/SLA.

## 2026-09-15 — Resume Gate approved

- User replied `继续`, approving the displayed simulated resume as this round's frozen interview surface.
- Manifest changed `resume_status` to `FROZEN` and `user_resume_review_status` to `APPROVED` before Red Wave 1 generation.
- User also refined checkpoint UX: show the complete resume in chat when useful; for Red/Blue 100-item batches, show only a few representative excerpts and one direct document link.

## 2026-09-15 — Red Wave 1

- Red input was restricted to the frozen `01_simulated_resume.md`, target role / interview stage, pinned `attack-model.md`, and general technical knowledge.
- Red did not read canonical Zuno docs, source, Evidence, or any Blue architecture notes.
- `02_red_questions.md` was generated with exactly 100 questions.
- The question set concentrates on six threads: project authenticity / ownership, Tool/MCP, direct routing, GraphRAG, Context/Memory, and Agent topology / fundamentals.
- The batch deliberately uses subtraction tests, ownership interrupts, evidence escalation, and project-to-fundamental bridges instead of treating the resume bullets as equally weighted checklist items.
- Red Wave 1 completed at commit `837142053351a7cfb1c4338ec6955d09c07ba196`.
- Workflow stopped at `BATCH_CHECKPOINT_RED_1`; Blue Wave 1 has not started.
