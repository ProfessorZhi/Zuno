# Zuno Documentation Architecture Reference

status: canonical-documentation-architecture
owner: Documentation Governance Owner

## 1. Canonical domains

```yaml
system_story:
  project:
    owns: [history, project_context, team_context, personal_ownership, project_unknowns]
  architecture:
    owns: [target_cross_cutting_architecture, authority_model, recovery_model]
  modules:
    owns: [target_responsibility_decomposition, module_contracts, module_state_and_recovery]
knowledge_control:
  decisions:
    owns: [accepted_design_rationale]
  evidence:
    owns: [current_code_test_trace_eval_runtime_evidence]
  governance:
    owns: [provenance, ownership_rules, documentation_rules, machine_routing, validation]
```

No seventh canonical domain may override these owners.

## 2. Human / Machine projection

```yaml
human_view:
  purpose: build_mental_model_and_support_interview_explanation
  preferred_content:
    - real_scenario
    - baseline
    - failure_of_baseline
    - design_causality
    - normal_flow
    - failure_and_recovery
    - tradeoff
    - simplification_condition
machine_view:
  purpose: implementation_review_and_agent_navigation
  preferred_content:
    - owner
    - authoritative_fact
    - contract
    - version
    - completion_proof
    - idempotency
    - persistence
    - retry_replan_reconcile
    - security
    - failure_matrix
    - source_map
```

Human prose may change structure. Machine reference may change indexing. Neither may change Architecture Owner, Authority, Contract semantics, Recovery semantics, Security Authority, Current/Target or Evidence level without the corresponding canonical change.

## 3. Truth layers

```text
History  -> project/
Target   -> architecture/ + modules/
Decision -> decisions/
Current  -> evidence/
Rules    -> governance/
```

Research is upstream input. Maintenance is workflow/history support. Neither becomes Current or Target by presence alone.

## 4. Module decomposition

The Documentation Architecture does not freeze module count.

Current module numbering is a Target Architecture baseline, not a documentation invariant. A module should exist only when a durable responsibility boundary justifies it. Merge/split requires architecture rationale, migration impact and semantic-alignment review.

## 5. Navigation contracts

Human default:

```text
docs/README.md
→ project/project.md
→ architecture/architecture.md Part A
→ modules/README.md
→ selected Module Part A
→ evidence/README.md
```

Agent implementation default:

```text
architecture/reference.md
→ architecture.md Part B
→ modules/reference.md
→ selected Module Part B/C
→ decisions/
→ evidence/
→ code/test/schema/migration
```

## 6. Current compatibility paths

`docs/research/`, `docs/maintenance/`, and `docs/terminology.md` remain at their current paths during migration to avoid broad link churn. Their semantic ownership is subordinate to the six canonical domains:

- research -> upstream reference for Project / Architecture;
- maintenance -> operational appendix under Governance responsibility;
- terminology -> cross-document vocabulary governed by Governance.

Physical migration is optional and must not duplicate facts.
