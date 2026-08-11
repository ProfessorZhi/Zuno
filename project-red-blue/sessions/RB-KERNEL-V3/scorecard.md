# RB-KERNEL-V3 Scorecard

## 逐题记录

| Question ID | Attack Area | Answer Defensibility (0-5) | Architecture / Project Fitness (0-5) | Severity | Gap Type | Evidence Missing | Stop Status |
|---|---|---:|---:|---|---|---|---|
| Q001 | HOST_SUBSTITUTION | 4 | 2 | P0 | BUILD_BUY_GAP | WorkBuddy contract fit spike | KNOWN_GAP |
| Q002 | HOST_SUBSTITUTION | 4 | 2 | P0 | OVERENGINEERING_GAP | A/B/C runtime benchmark | KNOWN_GAP |
| Q003 | HOST_SUBSTITUTION | 4 | 3 | P1 | MEASUREMENT_GAP | state reuse and re-reasoning measurements | EVIDENCE_REQUIRED |
| Q004 | HOST_SUBSTITUTION | 5 | 4 | P1 | UNSUPPORTED_CLAIM | exact WorkBuddy enterprise contract | PASS |
| Q005 | DOMAIN_KERNEL_MINIMALITY | 4 | 4 | P1 | OVERENGINEERING_GAP | canonical object decision record | EVIDENCE_REQUIRED |
| Q006 | DOMAIN_KERNEL_MINIMALITY | 4 | 4 | P1 | ARCHITECTURE_GAP | cross-run/legal task spike | EVIDENCE_REQUIRED |
| Q007 | DOMAIN_KERNEL_MINIMALITY | 5 | 4 | P2 | DOC_CLARIFY | no Current implementation | PASS |
| Q008 | DOMAIN_LIFECYCLE | 4 | 4 | P1 | ARCHITECTURE_GAP | dependency invalidation trace | EVIDENCE_REQUIRED |
| Q009 | DOMAIN_LIFECYCLE | 4 | 4 | P1 | SECURITY_GAP | proposal-to-owner write trace | EVIDENCE_REQUIRED |
| Q010 | CURRENT_REALITY | 5 | 1 | P0 | CURRENT_EVIDENCE_GAP | legal kernel code/migration/trace | KNOWN_GAP |
| Q011 | CURRENT_REALITY | 5 | 1 | P0 | CURRENT_EVIDENCE_GAP | legal domain/checkpoint E2E | KNOWN_GAP |
| Q012 | RETRIEVAL | 4 | 4 | P1 | BUILD_BUY_GAP | kill graph benchmark | EVIDENCE_REQUIRED |
| Q013 | RETRIEVAL | 4 | 4 | P1 | MEASUREMENT_GAP | graph cost/error buckets | EVIDENCE_REQUIRED |
| Q014 | MULTI_AGENT | 4 | 4 | P1 | OVERENGINEERING_GAP | L0-L3 comparison | EVIDENCE_REQUIRED |
| Q015 | MEMORY | 4 | 4 | P1 | OVERENGINEERING_GAP | memory ablation | EVIDENCE_REQUIRED |
| Q016 | RUNTIME | 4 | 4 | P0 | BUILD_BUY_GAP | runtime substitution spike | EVIDENCE_REQUIRED |
| Q017 | TOOL_RUNTIME | 4 | 4 | P1 | BUILD_BUY_GAP | MCP/API adapter and effect trace | EVIDENCE_REQUIRED |
| Q018 | DEPLOYMENT | 5 | 4 | P1 | OVERENGINEERING_GAP | workload/failure/scaling evidence | KNOWN_GAP |
| Q019 | SECURITY | 5 | 3 | P1 | SECURITY_GAP | attested security benchmark | EVIDENCE_REQUIRED |
| Q020 | SECURITY | 5 | 4 | P1 | UNSUPPORTED_CLAIM | WorkBuddy deployment evidence | KNOWN_GAP |
| Q021 | LEGAL_CAPABILITY | 4 | 4 | P1 | ARCHITECTURE_GAP | provider conformance spike | EVIDENCE_REQUIRED |
| Q022 | LEGAL_CAPABILITY | 5 | 4 | P0 | LICENSE_GAP | data/model/code license matrix | KNOWN_GAP |
| Q023 | BENCHMARK | 5 | 1 | P0 | MEASUREMENT_GAP | executed A/B/C results | KNOWN_GAP |
| Q024 | MINIMUM_ARCHITECTURE | 4 | 4 | P0 | BUILD_BUY_GAP | replacement cost and C>B result | KNOWN_GAP |

## Campaign Quality Profile

| Attack Area | question_count | avg_answer_defensibility | avg_architecture_project_fitness | p0_count | p1_count | unsupported_count | unsupported_rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| HOST_SUBSTITUTION | 4 | 4.25 | 2.75 | 2 | 2 | 2 | 0.50 |
| DOMAIN_KERNEL_MINIMALITY | 3 | 4.33 | 4.00 | 0 | 3 | 0 | 0.00 |
| DOMAIN_LIFECYCLE | 2 | 4.00 | 4.00 | 0 | 2 | 0 | 0.00 |
| CURRENT_REALITY | 2 | 5.00 | 1.00 | 2 | 0 | 0 | 0.00 |
| RETRIEVAL | 2 | 4.00 | 4.00 | 0 | 2 | 0 | 0.00 |
| MULTI_AGENT | 1 | 4.00 | 4.00 | 0 | 1 | 0 | 0.00 |
| MEMORY | 1 | 4.00 | 4.00 | 0 | 1 | 0 | 0.00 |
| RUNTIME | 1 | 4.00 | 4.00 | 1 | 0 | 0 | 0.00 |
| TOOL_RUNTIME | 1 | 4.00 | 4.00 | 0 | 1 | 0 | 0.00 |
| DEPLOYMENT | 1 | 5.00 | 4.00 | 0 | 1 | 0 | 0.00 |
| SECURITY | 2 | 5.00 | 3.50 | 0 | 2 | 2 | 1.00 |
| LEGAL_CAPABILITY | 2 | 4.50 | 4.00 | 1 | 1 | 0 | 0.00 |
| BENCHMARK | 1 | 5.00 | 1.00 | 1 | 0 | 0 | 0.00 |
| MINIMUM_ARCHITECTURE | 1 | 4.00 | 4.00 | 1 | 0 | 0 | 0.00 |

question_count: 24
avg_answer_defensibility: 4.38
avg_architecture_project_fitness: 3.33
p0_count: 8
p1_count: 16
unsupported_count: 4
unsupported_rate: 0.17

## Campaign Summary

coverage_status: COMPLETE_FOR_V3_SCOPE
p0_total: 8
p1_total: 16
reopened_gap_count: 0
decision: MINIMAL_DOMAIN_BACKEND_SURVIVES; NATIVE_RUNTIME_NOT_PROVEN

## Baseline Delta

- RB-ARCH-001 的 Build-vs-Buy gap 在 V3 被拆成 Host、Domain Backend、Runtime Provider、Retrieval、Memory、Tool、Deployment 七个独立杀伤面。
- V3 首次把 WorkBuddy 作为公平 A/B/C benchmark 的 Host 变体，并把针对 WorkBuddy 的安全负面断言从攻击选项中删除为无证据断言。
- V3 没有把法律对象列表、GraphRAG、Multi-Agent、Memory、Runtime 或微服务升级为 Current；所有未运行的收益保持 Hypothesis。
