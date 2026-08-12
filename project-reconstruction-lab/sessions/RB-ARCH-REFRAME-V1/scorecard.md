# RB-ARCH-REFRAME-V1 Scorecard

## 逐题记录

| Question ID | Attack Area | Answer Defensibility (0-5) | Architecture / Project Fitness (0-5) | Severity | Gap Type | Evidence Missing | Stop Status |
|---|---|---:|---:|---|---|---|---|
| Q001 | PYTHON_ONLY | 4 | 4 | P1 | ARCHITECTURE_GAP | cross-language cost benchmark | EVIDENCE_REQUIRED |
| Q002 | PYTHON_ONLY | 4 | 4 | P1 | PERFORMANCE_GAP | worker CPU/GPU measurements | EVIDENCE_REQUIRED |
| Q003 | PYTHON_ONLY | 4 | 4 | P1 | PERFORMANCE_GAP | workload profile and queue SLO | EVIDENCE_REQUIRED |
| Q004 | SERVICE_BOUNDARY | 4 | 4 | P0 | TARGET_CONSTRAINT | service boundary evidence | EVIDENCE_REQUIRED |
| Q005 | SERVICE_BOUNDARY | 5 | 5 | P0 | OVERENGINEERING_GAP | migration taxonomy proof | PASS |
| Q006 | SERVICE_BOUNDARY | 4 | 4 | P1 | SERVICE_BOUNDARY_GAP | edge scaling evidence | EVIDENCE_REQUIRED |
| Q007 | SERVICE_BOUNDARY | 4 | 5 | P0 | OWNERSHIP_GAP | domain write trace | EVIDENCE_REQUIRED |
| Q008 | SERVICE_BOUNDARY | 4 | 5 | P0 | RUNTIME_GAP | long-run service trace | EVIDENCE_REQUIRED |
| Q009 | SERVICE_BOUNDARY | 4 | 4 | P0 | SERVICE_BOUNDARY_GAP | knowledge worker SLO | EVIDENCE_REQUIRED |
| Q010 | SERVICE_BOUNDARY | 4 | 5 | P0 | SECURITY_GAP | sandbox isolation evidence | EVIDENCE_REQUIRED |
| Q011 | SERVICE_BOUNDARY | 5 | 4 | P1 | OVERENGINEERING_GAP | legal capability resource evidence | EVIDENCE_REQUIRED |
| Q012 | SERVICE_BOUNDARY | 4 | 4 | P1 | OVERENGINEERING_GAP | model gateway sharing evidence | EVIDENCE_REQUIRED |
| Q013 | SERVICE_BOUNDARY | 4 | 4 | P1 | OVERENGINEERING_GAP | eval worker lifecycle evidence | EVIDENCE_REQUIRED |
| Q014 | AGENT_RUNTIME | 5 | 4 | P0 | OVERENGINEERING_GAP | agent profile vs service test | EVIDENCE_REQUIRED |
| Q015 | DATA_OWNERSHIP | 5 | 5 | P0 | OWNERSHIP_GAP | domain/runtime reconcile trace | EVIDENCE_REQUIRED |
| Q016 | DATA_OWNERSHIP | 4 | 4 | P1 | DEPLOYMENT_GAP | schema isolation evidence | EVIDENCE_REQUIRED |
| Q017 | COMMUNICATION | 4 | 4 | P1 | COMMUNICATION_GAP | protocol latency/error matrix | EVIDENCE_REQUIRED |
| Q018 | COMMUNICATION | 4 | 3 | P1 | OPERATIONAL_GAP | tracing/retry cost | EVIDENCE_REQUIRED |
| Q019 | DEPLOYMENT | 5 | 4 | P1 | OVERENGINEERING_GAP | deployment profile evidence | EVIDENCE_REQUIRED |
| Q020 | DEPLOYMENT | 5 | 4 | P1 | OVERENGINEERING_GAP | real capacity/workload data | KNOWN_GAP |
| Q021 | DOC_TAXONOMY | 5 | 5 | P0 | DOC_GOVERNANCE_GAP | taxonomy migration | EVIDENCE_REQUIRED |
| Q022 | DOC_TAXONOMY | 5 | 5 | P0 | OWNERSHIP_GAP | canonical registry verifier | EVIDENCE_REQUIRED |
| Q023 | CURRENT_EVIDENCE | 5 | 1 | P0 | CURRENT_EVIDENCE_GAP | deployed service evidence | KNOWN_GAP |
| Q024 | CURRENT_EVIDENCE | 5 | 2 | P0 | DOC_GOVERNANCE_GAP | final verifier and link audit | EVIDENCE_REQUIRED |

## Campaign Quality Profile

| Attack Area | question_count | avg_answer_defensibility | avg_architecture_project_fitness | p0_count | p1_count | unsupported_count | unsupported_rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| PYTHON_ONLY | 3 | 4.00 | 4.00 | 0 | 3 | 0 | 0.00 |
| SERVICE_BOUNDARY | 10 | 4.40 | 4.40 | 6 | 4 | 0 | 0.00 |
| AGENT_RUNTIME | 1 | 5.00 | 4.00 | 1 | 0 | 0 | 0.00 |
| DATA_OWNERSHIP | 2 | 4.50 | 4.50 | 1 | 1 | 0 | 0.00 |
| COMMUNICATION | 2 | 4.00 | 3.50 | 0 | 2 | 0 | 0.00 |
| DEPLOYMENT | 2 | 5.00 | 4.00 | 0 | 2 | 0 | 0.00 |
| DOC_TAXONOMY | 2 | 5.00 | 5.00 | 2 | 0 | 0 | 0.00 |
| CURRENT_EVIDENCE | 2 | 5.00 | 1.50 | 2 | 0 | 0 | 0.00 |

question_count: 24
avg_answer_defensibility: 4.54
avg_architecture_project_fitness: 4.00
p0_count: 12
p1_count: 12
unsupported_count: 0
unsupported_rate: 0.00

## Campaign Summary

coverage_status: COMPLETE_FOR_REFRAME_SCOPE
p0_total: 11
p1_total: 13
reopened_gap_count: 0
decision: PYTHON_ONLY_AND_MICROSERVICE_TARGET_SURVIVE; SERVICE_COUNT_AND_TAXONOMY_REFRAMED

## Baseline Delta

- Python-only 与 Microservice 从“候选”变成用户确认的 Target Constraint；红队只保留边界、成本和证据攻击。
- 11 Logical Modules 不再是永久 Canonical Architecture；服务数量收敛为 5 个 network-facing Python services + worker profiles 的 Target 候选。
- Multi-Agent 保持开放，但 Agent profile 不自动等于微服务；Legal Intelligence、Model Gateway、Eval/Observability 等候选服务被压缩为 Provider/Worker，除非出现独立边界证据。
