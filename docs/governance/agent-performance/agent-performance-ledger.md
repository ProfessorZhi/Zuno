# Programming Agent Performance Ledger

Status: provisional review ledger

Scores are bound to the reviewed Head SHA and are not final until merge reconciliation.

| PR | Agent Shell | Provider / Visible Model | Work Package | Implementation Rounds | Repair Rounds | Reported Wall Clock | Total Tokens | Current CI | Reviewed Head | Decision | Current Score | Merge State |
|---:|---|---|---|---:|---:|---:|---:|---|---|---|---:|---|
| [#56](https://github.com/ProfessorZhi/Zuno/pull/56) | Antigravity | not reported / Gemini 3.6 Flash | `AG-PR56-FAIL-CLOSED-PAYLOAD-HARDENING` | 1 | 4+ | partially reported | not reported | success | `8cc0101af0214690387d3a187be3904b72070ccd` | `REQUEST_CHANGES` | 72 | Open Draft |
| [#57](https://github.com/ProfessorZhi/Zuno/pull/57) | Claude Code | MiniMax / MiniMax-M3 | `MM-PHASE22-BENCHMARK-PREFLIGHT-CONTRACT` | 1 | 0 | 8m 29s | not reported | failure | `e7e007d47f471610966201394b84ddc118814aff` | `REQUEST_CHANGES` | 80 | Open Draft; replacement required |
| [#58](https://github.com/ProfessorZhi/Zuno/pull/58) | Claude Code | DeepSeek / deepseek-v4-flash | `DS-PHASE22-RUNTIME-EVIDENCE-BINDING-CONTRACT` | 1 | 0 | 19m 31s | not reported | failure | `999d00a93734c02be26082116b4bc19673a179b3` | `REQUEST_CHANGES` | 83 | Open Draft; replacement required |

## Current task-fit observations

| Agent configuration | Stronger fit | Current risks |
|---|---|---|
| Antigravity + Gemini 3.6 Flash | Narrow repair tasks with explicit defect lists | Weak first-pass trust-boundary reasoning, Git-governance violations, report drift, multi-round convergence |
| Claude Code + MiniMax M3 | Deterministic modules, CLI, broad test matrices, fast scaffolding | State-semantics drift, oversized first draft, tests may lock in the implementation's own incorrect interpretation |
| Claude Code + DeepSeek V4 Flash | Deterministic validation contracts, disciplined scope, negative-path testing | Dynamic error-code leakage, subtle public-contract inconsistencies, did not proactively reconcile repository attribution rules |

This shared view is maintained by ChatGPT. Programming Agents update only their unique `records/pr-NNNN.json` file unless a finalization prompt explicitly authorizes a ledger reconciliation.
