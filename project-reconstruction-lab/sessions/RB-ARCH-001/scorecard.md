# RB-ARCH-001 Scorecard

## 逐题记录

| Question ID | Attack Area | Answer Defensibility (0-5) | Architecture / Project Fitness (0-5) | Severity | Gap Type | Evidence Missing | Stop Status |
|---|---|---:|---:|---|---|---|---|
| Q001 | PROJECT_BACKGROUND | 1 | 1 | P0 | PROJECT_REALITY_GAP | project origin, requester, user | KNOWN_GAP |
| Q002 | PROJECT_BACKGROUND | 1 | 1 | P0 | BACKGROUND_GAP | As-Is workflow and human baseline | KNOWN_GAP |
| Q003 | PROJECT_BACKGROUND | 2 | 1 | P0 | RECONSTRUCTION_CONFIDENCE_GAP | direct project link for school/court clues | KNOWN_GAP |
| Q004 | PROJECT_BACKGROUND | 1 | 1 | P0 | PROJECT_ARCHITECTURE_ALIGNMENT_GAP | historical need vs Legal Target link | KNOWN_GAP |
| Q005 | PROJECT_BACKGROUND | 2 | 2 | P1 | PROJECT_ARCHITECTURE_ALIGNMENT_GAP | non-legal historical task | KNOWN_GAP |
| Q006 | PROJECT_BACKGROUND | 1 | 2 | P1 | OVERENGINEERING_GAP | real V0/V1 scope and baseline | KNOWN_GAP |
| Q007 | PRODUCT_VALUE | 2 | 2 | P1 | PRODUCT_POSITIONING_GAP | user outcome and baseline | KNOWN_GAP |
| Q008 | PRODUCT_VALUE | 4 | 3 | P1 | OVERENGINEERING_GAP | proof of actual task complexity | EVIDENCE_REQUIRED |
| Q009 | PRODUCT_VALUE | 4 | 4 | P2 | DOC_CLARIFY | no blocking Target evidence | PASS |
| Q010 | PRODUCT_VALUE | 3 | 4 | P1 | CURRENT_EVIDENCE_GAP | immutable version runtime trace | EVIDENCE_REQUIRED |
| Q011 | PRODUCT_VALUE | 4 | 4 | P2 | OVERENGINEERING_GAP | task routing evidence | PASS |
| Q012 | COMPETITOR | 3 | 2 | P1 | BUILD_BUY_GAP | competitor Contract/Fit evidence | KNOWN_GAP |
| Q013 | COMPETITOR | 3 | 3 | P1 | BUILD_BUY_GAP | Adapter conformance spike | EVIDENCE_REQUIRED |
| Q014 | COMPETITOR | 4 | 3 | P1 | BUILD_BUY_GAP | fixed corpus and license/ops test | EVIDENCE_REQUIRED |
| Q015 | COMPETITOR | 4 | 3 | P1 | BUILD_BUY_GAP | source-level modification map | EVIDENCE_REQUIRED |
| Q016 | COMPETITOR | 2 | 2 | P1 | BUILD_BUY_GAP | final ADOPT/EXTEND/BUILD/DEFER matrix | KNOWN_GAP |
| Q017 | COMPETITOR | 3 | 4 | P1 | CURRENT_EVIDENCE_GAP | provider adapter and canonical write trace | EVIDENCE_REQUIRED |
| Q018 | OWNERSHIP | 1 | 1 | P0 | OWNERSHIP_GAP | team size and roles | KNOWN_GAP |
| Q019 | OWNERSHIP | 1 | 1 | P0 | RESUME_CLAIM_RISK | personal commits/tasks | KNOWN_GAP |
| Q020 | OWNERSHIP | 1 | 1 | P0 | DELIVERY_PROCESS_GAP | decision/review/release chain | KNOWN_GAP |
| Q021 | OWNERSHIP | 1 | 2 | P1 | DELIVERY_PROCESS_GAP | historical capability evolution | KNOWN_GAP |
| Q022 | OWNERSHIP | 2 | 2 | P1 | OVERENGINEERING_GAP | team and physical deployment scale | KNOWN_GAP |
| Q023 | OWNERSHIP | 1 | 1 | P1 | OWNERSHIP_GAP | handover/on-call/substitute evidence | KNOWN_GAP |
| Q024 | DEVELOPMENT_PROCESS | 1 | 1 | P1 | DELIVERY_PROCESS_GAP | baseline, review, release, rollback | KNOWN_GAP |
| Q025 | DEVELOPMENT_PROCESS | 1 | 1 | P1 | PROJECT_ARCHITECTURE_ALIGNMENT_GAP | need-failure-decision chain | KNOWN_GAP |
| Q026 | ARCHITECTURE | 4 | 4 | P2 | DOC_CLARIFY | no Target gap | PASS |
| Q027 | ARCHITECTURE | 3 | 4 | P1 | CURRENT_EVIDENCE_GAP | owner commit/transaction evidence | EVIDENCE_REQUIRED |
| Q028 | ARCHITECTURE | 3 | 4 | P1 | FAILURE_RECOVERY_GAP | reconciliation trace and test | EVIDENCE_REQUIRED |
| Q029 | ARCHITECTURE | 4 | 4 | P2 | DOC_CLARIFY | no Target gap | PASS |
| Q030 | ARCHITECTURE | 4 | 4 | P1 | CURRENT_EVIDENCE_GAP | single-controller runtime trace | EVIDENCE_REQUIRED |
| Q031 | ARCHITECTURE | 4 | 4 | P2 | DOC_CLARIFY | no Target gap | PASS |
| Q032 | ARCHITECTURE | 3 | 4 | P1 | FAILURE_RECOVERY_GAP | plan barrier and epoch test | EVIDENCE_REQUIRED |
| Q033 | ARCHITECTURE | 4 | 4 | P2 | DOC_CLARIFY | no Target gap | PASS |
| Q034 | ARCHITECTURE | 3 | 4 | P1 | FAILURE_RECOVERY_GAP | provider effect reconciliation | EVIDENCE_REQUIRED |
| Q035 | ARCHITECTURE | 4 | 4 | P2 | DOC_CLARIFY | no Target gap | PASS |
| Q036 | ARCHITECTURE | 4 | 4 | P1 | PROJECT_ARCHITECTURE_ALIGNMENT_GAP | historical domain alignment | KNOWN_GAP |
| Q037 | MODEL | 1 | 2 | P0 | PROJECT_REALITY_GAP | provider/deployment mode | KNOWN_GAP |
| Q038 | MODEL | 3 | 3 | P1 | CURRENT_EVIDENCE_GAP | residency/GPU/provider evidence | EVIDENCE_REQUIRED |
| Q039 | MODEL | 4 | 4 | P1 | CURRENT_EVIDENCE_GAP | routing config and trace | EVIDENCE_REQUIRED |
| Q040 | MODEL | 4 | 4 | P2 | DOC_CLARIFY | index/model compatibility proof | EVIDENCE_REQUIRED |
| Q041 | MODEL | 3 | 4 | P1 | CURRENT_EVIDENCE_GAP | model attempt/usage trace | EVIDENCE_REQUIRED |
| Q042 | FINE_TUNING | 1 | 1 | P0 | PROJECT_REALITY_GAP | training and experiment records | KNOWN_GAP |
| Q043 | FINE_TUNING | 4 | 4 | P2 | DOC_CLARIFY | no historical claim made | PASS |
| Q044 | FINE_TUNING | 3 | 3 | P1 | MEASUREMENT_GAP | dataset and split evidence | EVIDENCE_REQUIRED |
| Q045 | FINE_TUNING | 4 | 4 | P1 | MEASUREMENT_GAP | baseline/ablation/cost | EVIDENCE_REQUIRED |
| Q046 | DEPLOYMENT | 1 | 1 | P0 | PROJECT_REALITY_GAP | environment, users, acceptance | KNOWN_GAP |
| Q047 | DEPLOYMENT | 3 | 3 | P0 | CURRENT_EVIDENCE_GAP | code/trace/runtime evidence | EVIDENCE_REQUIRED |
| Q048 | DEPLOYMENT | 3 | 4 | P1 | OVERENGINEERING_GAP | actual scale and deployment | KNOWN_GAP |
| Q049 | DEPLOYMENT | 3 | 4 | P1 | FAILURE_RECOVERY_GAP | ingestion crash/replay evidence | EVIDENCE_REQUIRED |
| Q050 | DEPLOYMENT | 4 | 4 | P1 | CURRENT_EVIDENCE_GAP | parser/version runtime evidence | EVIDENCE_REQUIRED |
| Q051 | RAG | 4 | 4 | P2 | DOC_CLARIFY | no Target gap | PASS |
| Q052 | RAG | 4 | 4 | P2 | DOC_CLARIFY | no Target gap | PASS |
| Q053 | RAG | 3 | 4 | P1 | IMPLEMENTATION_DEPTH_GAP | K/N/M and threshold experiment | EVIDENCE_REQUIRED |
| Q054 | RAG | 4 | 4 | P1 | BUILD_BUY_GAP | conditional graph benchmark | EVIDENCE_REQUIRED |
| Q055 | RAG | 3 | 4 | P1 | MEASUREMENT_GAP | graph extraction error eval | EVIDENCE_REQUIRED |
| Q056 | RAG | 4 | 4 | P2 | DOC_CLARIFY | no Target gap | PASS |
| Q057 | RAG | 4 | 4 | P2 | DOC_CLARIFY | no Target gap | PASS |
| Q058 | RAG | 4 | 4 | P1 | MEASUREMENT_GAP | stop-reason distribution and eval | EVIDENCE_REQUIRED |
| Q059 | MEMORY | 4 | 4 | P2 | DOC_CLARIFY | no Target gap | PASS |
| Q060 | MEMORY | 4 | 4 | P2 | DOC_CLARIFY | no Target gap | PASS |
| Q061 | MEMORY | 4 | 4 | P2 | DOC_CLARIFY | no Target gap | PASS |
| Q062 | MEMORY | 4 | 4 | P1 | SECURITY_GAP | authority and scope test | EVIDENCE_REQUIRED |
| Q063 | MEMORY | 3 | 4 | P1 | CURRENT_EVIDENCE_GAP | quarantine/projection test | EVIDENCE_REQUIRED |
| Q064 | MEMORY | 4 | 4 | P1 | IMPLEMENTATION_DEPTH_GAP | recall/context budget evidence | EVIDENCE_REQUIRED |
| Q065 | AGENT | 4 | 4 | P2 | DOC_CLARIFY | no Target gap | PASS |
| Q066 | AGENT | 4 | 4 | P1 | PROJECT_ARCHITECTURE_ALIGNMENT_GAP | real review task template | KNOWN_GAP |
| Q067 | AGENT | 4 | 4 | P2 | DOC_CLARIFY | no Target gap | PASS |
| Q068 | AGENT | 3 | 4 | P1 | FAILURE_RECOVERY_GAP | epoch/replan trace | EVIDENCE_REQUIRED |
| Q069 | AGENT | 4 | 4 | P1 | ARCHITECTURE_GAP | capability failure contract evidence | EVIDENCE_REQUIRED |
| Q070 | AGENT | 4 | 4 | P1 | SECURITY_GAP | context assembly and authorization trace | EVIDENCE_REQUIRED |
| Q071 | AGENT | 4 | 4 | P2 | DOC_CLARIFY | no Target gap | PASS |
| Q072 | TOOL | 4 | 4 | P2 | DOC_CLARIFY | no Target gap | PASS |
| Q073 | TOOL | 4 | 4 | P1 | CURRENT_EVIDENCE_GAP | onboarding/grant/selection trace | EVIDENCE_REQUIRED |
| Q074 | TOOL | 4 | 4 | P1 | SECURITY_GAP | grant lineage implementation | EVIDENCE_REQUIRED |
| Q075 | TOOL | 4 | 4 | P1 | SECURITY_GAP | version/approval/epoch test | EVIDENCE_REQUIRED |
| Q076 | TOOL | 3 | 4 | P0 | FAILURE_RECOVERY_GAP | provider conformance and manual reconciliation | EVIDENCE_REQUIRED |
| Q077 | INFRA | 3 | 3 | P1 | FUNDAMENTAL_GAP | actual MQ usage and idempotency | EVIDENCE_REQUIRED |
| Q078 | INFRA | 4 | 4 | P2 | DOC_CLARIFY | no Target gap | PASS |
| Q079 | INFRA | 3 | 4 | P1 | FAILURE_RECOVERY_GAP | lease parameters and fault test | EVIDENCE_REQUIRED |
| Q080 | INFRA | 3 | 3 | P1 | FUNDAMENTAL_GAP | actual runtime language/worker | KNOWN_GAP |
| Q081 | INFRA | 3 | 4 | P1 | MEASUREMENT_GAP | load and quota benchmark | EVIDENCE_REQUIRED |
| Q082 | INFRA | 4 | 4 | P2 | DOC_CLARIFY | no Target gap | PASS |
| Q083 | SECURITY | 4 | 4 | P1 | SECURITY_GAP | authorization execution trace | EVIDENCE_REQUIRED |
| Q084 | SECURITY | 4 | 4 | P1 | SECURITY_GAP | injection/taint test | EVIDENCE_REQUIRED |
| Q085 | SECURITY | 4 | 4 | P1 | SECURITY_GAP | revocation propagation test | EVIDENCE_REQUIRED |
| Q086 | SECURITY | 4 | 4 | P1 | SECURITY_GAP | separate decision audit evidence | EVIDENCE_REQUIRED |
| Q087 | SECURITY | 4 | 4 | P1 | SECURITY_GAP | pre-retrieval filtering test | EVIDENCE_REQUIRED |
| Q088 | EVAL | 2 | 3 | P1 | MEASUREMENT_GAP | baseline/dataset/metrics | KNOWN_GAP |
| Q089 | EVAL | 4 | 4 | P2 | DOC_CLARIFY | no Target gap | PASS |
| Q090 | EVAL | 3 | 4 | P1 | MEASUREMENT_GAP | artifact promotion/shadow/rollback | EVIDENCE_REQUIRED |
| Q091 | EVAL | 4 | 4 | P1 | MEASUREMENT_GAP | feedback governance evidence | EVIDENCE_REQUIRED |
| Q092 | PRODUCTION | 1 | 1 | P0 | PROJECT_REALITY_GAP | users, environment, acceptance | KNOWN_GAP |
| Q093 | PRODUCTION | 1 | 1 | P1 | MEASUREMENT_GAP | trace, bill, benchmark, feedback | KNOWN_GAP |
| Q094 | PRODUCTION | 4 | 4 | P1 | CURRENT_EVIDENCE_GAP | current implementation inventory | EVIDENCE_REQUIRED |
| Q095 | PRODUCTION | 4 | 4 | P1 | OVERENGINEERING_GAP | scope-down decision evidence | KNOWN_GAP |
| Q096 | RESUME | 1 | 1 | P0 | RESUME_CLAIM_RISK | confirmed personal scope | KNOWN_GAP |
| Q097 | RESUME | 1 | 1 | P0 | RESUME_CLAIM_RISK | personal Graph work evidence | KNOWN_GAP |
| Q098 | RESUME | 3 | 3 | P0 | RESUME_CLAIM_RISK | Memory/model/deployment ownership | KNOWN_GAP |
| Q099 | RESUME | 3 | 3 | P0 | NARRATIVE_GAP | user-confirmed project narrative | KNOWN_GAP |
| Q100 | RESUME | 4 | 4 | P0 | PROJECT_REALITY_GAP | fact gate and architecture gate | KNOWN_GAP |

## Campaign Quality Profile

按 Attack Area 聚合；平均值只用于定位，不产生单一总分。

| Attack Area | question_count | avg_answer_defensibility | avg_architecture_project_fitness | P0_count | P1_count | unsupported_count | unsupported_rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| PROJECT_BACKGROUND | 6 | 1.3 | 1.3 | 4 | 2 | 0 | 0% |
| PRODUCT_VALUE | 5 | 3.4 | 3.4 | 0 | 3 | 0 | 0% |
| COMPETITOR | 6 | 3.2 | 2.8 | 0 | 6 | 0 | 0% |
| OWNERSHIP | 6 | 1.2 | 1.3 | 3 | 3 | 0 | 0% |
| DEVELOPMENT_PROCESS | 2 | 1.0 | 1.0 | 0 | 2 | 0 | 0% |
| ARCHITECTURE | 11 | 3.6 | 4.0 | 0 | 6 | 0 | 0% |
| MODEL | 5 | 3.0 | 3.4 | 1 | 3 | 0 | 0% |
| FINE_TUNING | 4 | 3.0 | 3.0 | 1 | 2 | 0 | 0% |
| DEPLOYMENT | 5 | 2.8 | 3.2 | 2 | 3 | 0 | 0% |
| RAG | 8 | 3.8 | 4.0 | 0 | 4 | 0 | 0% |
| MEMORY | 6 | 3.8 | 4.0 | 0 | 3 | 0 | 0% |
| AGENT | 7 | 3.9 | 4.0 | 0 | 4 | 0 | 0% |
| TOOL | 5 | 3.8 | 4.0 | 1 | 3 | 0 | 0% |
| INFRA | 6 | 3.3 | 3.7 | 0 | 4 | 0 | 0% |
| SECURITY | 5 | 4.0 | 4.0 | 0 | 5 | 0 | 0% |
| EVAL | 4 | 3.3 | 3.8 | 0 | 3 | 0 | 0% |
| PRODUCTION | 4 | 2.5 | 2.5 | 1 | 3 | 0 | 0% |
| RESUME | 5 | 2.4 | 2.4 | 5 | 0 | 0 | 0% |

## Campaign Summary

- coverage_status: `SUFFICIENT`
- P0_total: 18
- P1_total: 59
- unsupported_rate: 0%
- reopened_gap_count: 0
- question_budget: 100
- actual_question_count: 100
- stop_reason: `QUESTION_BUDGET_REACHED_AFTER_CLOSED_LOOP`
- Fundamental questions were used as transitions and recorded separately from Project Gaps; they did not prove historical implementation.
- The campaign did not produce a single Zuno total score.

## Baseline Delta

baseline_session_id: RB-ARCH-001

This is the first baseline campaign. There is no prior canonical red/blue session, so delta is `N/A`, not fabricated as zero.

| Attack Area | Baseline | Current | Delta |
|---|---:|---:|---:|
| PROJECT_BACKGROUND | N/A | 1.3 | N/A |
| PRODUCT_VALUE | N/A | 3.4 | N/A |
| COMPETITOR | N/A | 3.2 | N/A |
| OWNERSHIP | N/A | 1.2 | N/A |
| DEVELOPMENT_PROCESS | N/A | 1.0 | N/A |
| ARCHITECTURE | N/A | 3.6 | N/A |
| MODEL | N/A | 3.0 | N/A |
| FINE_TUNING | N/A | 3.0 | N/A |
| DEPLOYMENT | N/A | 2.8 | N/A |
| RAG | N/A | 3.8 | N/A |
| MEMORY | N/A | 3.8 | N/A |
| AGENT | N/A | 3.9 | N/A |
| TOOL | N/A | 3.8 | N/A |
| INFRA | N/A | 3.3 | N/A |
| SECURITY | N/A | 4.0 | N/A |
| EVAL | N/A | 3.3 | N/A |
| PRODUCTION | N/A | 2.5 | N/A |
| RESUME | N/A | 2.4 | N/A |
