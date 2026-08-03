"""Generate the 80-case synthetic benchmark deterministically from the world model.

Output:
  - synthetic_cases.jsonl (one JSON object per line, 80 cases)
  - case_set_manifest.json (aggregate manifest)

Stratification:
  - 20 single-document fact
  - 20 cross-document multi-hop
  - 15 graph (path/relation/community)
  - 10 version/time/conflict
  - 5 no-answer (must abstain)
  - 5 permission/sensitive (deny or restricted)
  - 5 fault/partial-index (controlled behavior)

Each case carries the full required field set per the PHASE22 synthetic
benchmark contract:

  case_id, question, question_type, difficulty, expected_answer/expected_outcome,
  gold_document_refs, gold_source_spans, gold_evidence_refs,
  citation_ground_truth, required_relations, security_scope, effective_time,
  answer_policy, hard_negative_refs, provenance, generation_seed,
  world_model_hash, corpus_snapshot_hash.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SEED = "phase22-synthetic-2026-08-03-auroralis-v1"

CASES: list[dict] = []


def _h(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _evidence(doc_id: str, version: str, effective_at: str, span_text: str, source_topic_ref: str) -> dict:
    return {
        "doc_id": doc_id,
        "doc_version": version,
        "effective_at": effective_at,
        "source_span": span_text,
        "topic_ref": source_topic_ref,
    }


def _case(*, case_id, question, question_type, difficulty, expected_answer,
          gold_document_refs, gold_source_spans, gold_evidence_refs,
          required_relations, security_scope, effective_time, answer_policy,
          hard_negative_refs, expected_outcome=None, citation_ground_truth=None,
          difficulty_rationale=""):
    CASES.append({
        "case_id": case_id,
        "question": question,
        "question_type": question_type,
        "difficulty": difficulty,
        "expected_answer": expected_answer,
        "expected_outcome": expected_outcome if expected_outcome is not None else "answer",
        "gold_document_refs": list(gold_document_refs),
        "gold_source_spans": list(gold_source_spans),
        "gold_evidence_refs": list(gold_evidence_refs),
        "citation_ground_truth": citation_ground_truth if citation_ground_truth is not None else [
            {"doc_id": d, "source_span": s} for d, s in zip(gold_document_refs, gold_source_spans)
        ],
        "required_relations": list(required_relations),
        "security_scope": security_scope,
        "effective_time": effective_time,
        "answer_policy": answer_policy,
        "hard_negative_refs": list(hard_negative_refs),
        "provenance": {
            "world_model_id": "wm_auroralis_v1",
            "corpus_id": "corpus_auroralis_v1",
            "graph_id": "graph_auroralis_v1",
            "generation_seed": SEED,
            "fictional_disclaimer": "All facts derive from the synthetic Auroralis world model. No real companies, individuals, or web facts are referenced.",
            "difficulty_rationale": difficulty_rationale,
        },
    })


# ===========================================================================
# 1. SINGLE-DOCUMENT FACT (20)
# ===========================================================================

_case(case_id="syn_001", question="What is the release version of the Axis-9 Industrial Controller and on what date was it released?",
      question_type="single_doc_fact", difficulty="easy",
      expected_answer="Axis-9 Industrial Controller v9.4.0 was released on 2025-11-12.",
      gold_document_refs=["doc_axis9_release_notes"],
      gold_source_spans=["v9.4.0", "2025-11-12"],
      gold_evidence_refs=[_evidence("doc_axis9_release_notes", "v9.4.0", "2025-11-12", "v9.4.0", "prod_axis_9")],
      required_relations=[],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=["doc_axis8_eol_memo"],
      difficulty_rationale="Single fact answer in one release-notes doc; must disambiguate from Axis-8 EOL memo.")

_case(case_id="syn_002", question="Which Auroralis division is led by Iris Vange, and in which region does it operate?",
      question_type="single_doc_fact", difficulty="easy",
      expected_answer="Automation Systems (EMEA), led by Iris Vange.",
      gold_document_refs=["doc_org_chart_2026", "doc_iris_bio"],
      gold_source_spans=["Automation Systems", "Iris Vange", "Iris Vange"],
      gold_evidence_refs=[
          _evidence("doc_org_chart_2026", "v2026.Q2", "2026-04-01", "Automation Systems", "div_auto"),
          _evidence("doc_iris_bio", "v1.0", "2025-12-15", "Iris Vange", "emp_iris_vange"),
      ],
      required_relations=[],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=["doc_yui_bio", "doc_marcus_bio"],
      difficulty_rationale="Direct org-chart lookup; hard negatives are other president bios.")

_case(case_id="syn_003", question="Who is the Head of Procurement at Auroralis, and to whom does this person report?",
      question_type="single_doc_fact", difficulty="easy",
      expected_answer="Lukas Wenger is the Head of Procurement and reports to Solveig Hagen.",
      gold_document_refs=["doc_org_chart_2026", "doc_lukas_bio"],
      gold_source_spans=["Lukas Wenger", "Lukas Wenger", "Head of Procurement"],
      gold_evidence_refs=[
          _evidence("doc_org_chart_2026", "v2026.Q2", "2026-04-01", "Lukas Wenger", "emp_lukas_wenger"),
          _evidence("doc_lukas_bio", "v1.0", "2025-12-15", "Solveig Hagen", "emp_solveig_hagen"),
      ],
      required_relations=[],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=["doc_amani_bio", "doc_nadya_bio"],
      difficulty_rationale="Org-chart lookup; distractor bios are different directors.")

_case(case_id="syn_004", question="What is the v9.4.0 release of Axis-9 primarily known for, and who signed it off?",
      question_type="single_doc_fact", difficulty="medium",
      expected_answer="Axis-9 v9.4.0 introduces deterministic motion-control scheduling and a hardened CIP safety stack; signed off by Haruto Soma.",
      gold_document_refs=["doc_axis9_release_notes"],
      gold_source_spans=["deterministic motion-control scheduling", "hardened CIP safety stack", "Haruto Soma"],
      gold_evidence_refs=[_evidence("doc_axis9_release_notes", "v9.4.0", "2025-11-12", "Haruto Soma", "evt_axis_9_release")],
      required_relations=[],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=["doc_axis8_eol_memo", "doc_lumen_e2_release_notes"],
      difficulty_rationale="Multiple facts in one doc; must avoid Lumen-E2 release notes.")

_case(case_id="syn_005", question="What is the planned end-of-life date for the Axis-8 Industrial Controller?",
      question_type="single_doc_fact", difficulty="easy",
      expected_answer="Axis-8 EOL is planned for 2027-06-30.",
      gold_document_refs=["doc_axis8_eol_memo"],
      gold_source_spans=["2027-06-30", "end-of-life"],
      gold_evidence_refs=[_evidence("doc_axis8_eol_memo", "v1.0", "2026-03-01", "2027-06-30", "prod_axis_8")],
      required_relations=[],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=["doc_lumen_e1_eol_memo"],
      difficulty_rationale="Direct date extraction; distractors include Lumen-E1 EOL memo.")

_case(case_id="syn_006", question="What is the European headquarters city for Auroralis?",
      question_type="single_doc_fact", difficulty="easy",
      expected_answer="Reykjavik (Iceland).",
      gold_document_refs=["doc_org_chart_2026"],
      gold_source_spans=["Auroralis is led by CEO Kjartan Eliasson", "Auroralis is led by CEO Kjartan Eliasson"],
      gold_evidence_refs=[_evidence("doc_org_chart_2026", "v2026.Q2", "2026-04-01", "Reykjavik", "company")],
      required_relations=[],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=[],
      difficulty_rationale="Direct attribute of company in org chart.")

_case(case_id="syn_007", question="What is the total contract value (in EUR) of the v3 Helion Motors supply agreement?",
      question_type="single_doc_fact", difficulty="medium",
      expected_answer="EUR 12,500,000.",
      gold_document_refs=["doc_helion_contract"],
      gold_source_spans=["12,500,000"],
      gold_evidence_refs=[_evidence("doc_helion_contract", "v3", "2024-01-15", "12,500,000", "ct_helion_2024")],
      required_relations=[],
      security_scope="perm_div_auto_confidential", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=["doc_kobal_contract", "doc_polaris_contract_v2"],
      difficulty_rationale="Restricted doc; distractor contracts have similar values.")

_case(case_id="syn_008", question="On what date did the 2026 Information Security Policy become effective, and which prior edition does it supersede?",
      question_type="single_doc_fact", difficulty="medium",
      expected_answer="Effective 2026-01-01; supersedes the 2024 Edition (v4.1).",
      gold_document_refs=["doc_security_policy_2026"],
      gold_source_spans=["2026-01-01", "Supersedes"],
      gold_evidence_refs=[
          _evidence("doc_security_policy_2026", "v4.2", "2026-01-01", "2026-01-01", "pol_sec_2026"),
          _evidence("doc_security_policy_2024", "v4.1", "2024-01-01", "v4.1", "pol_sec_2024"),
      ],
      required_relations=[],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=[],
      difficulty_rationale="Time-bound fact with supersession.")

_case(case_id="syn_009", question="Who owns the Export Control and Trade Compliance Policy?",
      question_type="single_doc_fact", difficulty="easy",
      expected_answer="Amani Bello (General Counsel).",
      gold_document_refs=["doc_export_policy"],
      gold_source_spans=["Amani Bello", "General Counsel"],
      gold_evidence_refs=[_evidence("doc_export_policy", "v1.5", "2025-02-01", "Amani Bello", "emp_amani_bello")],
      required_relations=[],
      security_scope="perm_legal_privileged", effective_time="2026-08-03",
      answer_policy="answer_with_citation_restricted",
      hard_negative_refs=["doc_security_policy_2026", "doc_quality_policy"],
      difficulty_rationale="Policy owner lookup; doc is restricted but owner is global.")

_case(case_id="syn_010", question="What is the start date of Project Northwind, and which CEO sponsors it?",
      question_type="single_doc_fact", difficulty="medium",
      expected_answer="Started 2025-09-01; sponsored by CEO Kjartan Eliasson.",
      gold_document_refs=["doc_northwind_charter"],
      gold_source_spans=["2025-09-01", "Kjartan Eliasson"],
      gold_evidence_refs=[_evidence("doc_northwind_charter", "v1.2", "2025-09-01", "2025-09-01", "proj_northwind")],
      required_relations=[],
      security_scope="perm_div_auto_confidential", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=["doc_lumenx_charter", "doc_forge2_charter"],
      difficulty_rationale="Distractor project charters with different sponsors.")

_case(case_id="syn_011", question="What is the volume (in EUR) of the Polaris Steel MSA v2 (2025 Edition)?",
      question_type="single_doc_fact", difficulty="easy",
      expected_answer="EUR 5,750,000.",
      gold_document_refs=["doc_polaris_contract_v2"],
      gold_source_spans=["5,750,000"],
      gold_evidence_refs=[_evidence("doc_polaris_contract_v2", "v2", "2025-09-01", "5,750,000", "ct_polaris_2025")],
      required_relations=[],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=["doc_polaris_contract_v1", "doc_meridian_contract"],
      difficulty_rationale="Disambiguate v1 (EUR 5.1M) from v2 (EUR 5.75M).")

_case(case_id="syn_012", question="Which product is Haruto Soma the primary owner of, and which division does it belong to?",
      question_type="single_doc_fact", difficulty="medium",
      expected_answer="Axis-9 Industrial Controller (prod_axis_9) and Northwind Industrial SDK (prod_northwind_sdk), Automation Systems division.",
      gold_document_refs=["doc_axis9_release_notes", "doc_northwind_sdk_overview"],
      gold_source_spans=["Haruto Soma", "Haruto Soma"],
      gold_evidence_refs=[
          _evidence("doc_axis9_release_notes", "v9.4.0", "2025-11-12", "Haruto Soma", "prod_axis_9"),
          _evidence("doc_northwind_sdk_overview", "v3.0.0", "2026-01-15", "Haruto Soma", "prod_northwind_sdk"),
      ],
      required_relations=[],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=["doc_lumen_e2_release_notes", "doc_forge_x1_release_notes"],
      difficulty_rationale="Owner across multiple docs.")

_case(case_id="syn_013", question="What corrective action did Quality issue on 2026-04-22?",
      question_type="single_doc_fact", difficulty="medium",
      expected_answer="A voluntary firmware corrective action for the Forge-X1 v1.3.x powder feed subsystem.",
      gold_document_refs=["doc_forge_x1_recall_bulletin"],
      gold_source_spans=["powder feed", "2026-04-22", "Nadya Soroka"],
      gold_evidence_refs=[_evidence("doc_forge_x1_recall_bulletin", "v1.0", "2026-04-22", "2026-04-22", "evt_forge_x1_recall")],
      required_relations=[],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=["doc_axis8_eol_memo"],
      difficulty_rationale="Direct recall bulletin lookup.")

_case(case_id="syn_014", question="What is the CEO tenure start date?",
      question_type="single_doc_fact", difficulty="easy",
      expected_answer="2015-01-05.",
      gold_document_refs=["doc_ceo_bio"],
      gold_source_spans=["2015-01-05"],
      gold_evidence_refs=[_evidence("doc_ceo_bio", "v1.0", "2025-12-15", "2015-01-05", "ceo_kjartan_eli")],
      required_relations=[],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=[],
      difficulty_rationale="Direct attribute.")

_case(case_id="syn_015", question="Which supplier is in 'probation' preferred status, and what category does it serve?",
      question_type="single_doc_fact", difficulty="medium",
      expected_answer="Ozone Chemicals Ltd. (specialty chemicals).",
      gold_document_refs=["doc_supplier_brief_sup_ozone_chem"],
      gold_source_spans=["probation", "specialty chemicals"],
      gold_evidence_refs=[_evidence("doc_supplier_brief_sup_ozone_chem", "v1.0", "2025-12-01", "probation", "sup_ozone_chem")],
      required_relations=[],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=["doc_supplier_brief_sup_polaris_steel"],
      difficulty_rationale="Distractor is 'conditional' status.")

_case(case_id="syn_016", question="What is the Forge-X1 Field Service patch adoption rate by 2026-06-30?",
      question_type="single_doc_fact", difficulty="medium",
      expected_answer="87% patch adoption by 2026-06-30.",
      gold_document_refs=["doc_forge_x1_field_log"],
      gold_source_spans=["87%", "2026-06-30"],
      gold_evidence_refs=[_evidence("doc_forge_x1_field_log", "v1.0", "2026-06-30", "87%", "prod_forge_x1")],
      required_relations=[],
      security_scope="perm_div_auto_confidential", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=["doc_forge_x1_recall_bulletin"],
      difficulty_rationale="Restricted doc; need adoption rate from field log.")

_case(case_id="syn_017", question="List all directly-reporting divisions to the CEO.",
      question_type="single_doc_fact", difficulty="easy",
      expected_answer="Automation Systems, Edge Compute, Additive Manufacturing, Corporate Services.",
      gold_document_refs=["doc_org_chart_2026"],
      gold_source_spans=["Automation Systems", "Edge Compute", "Additive Manufacturing", "Corporate Services"],
      gold_evidence_refs=[_evidence("doc_org_chart_2026", "v2026.Q2", "2026-04-01", "Automation Systems", "divisions")],
      required_relations=[],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=[],
      difficulty_rationale="Multi-entity list extraction.")

_case(case_id="syn_018", question="Which Q2 2026 status report identifies the Kobal Silicon supplier qualification gap?",
      question_type="single_doc_fact", difficulty="medium",
      expected_answer="Project Lumen-X Q2 2026 Status Report.",
      gold_document_refs=["doc_lumenx_status_2026_q2"],
      gold_source_spans=["Kobal Silicon", "qualification gap"],
      gold_evidence_refs=[_evidence("doc_lumenx_status_2026_q2", "v1.0", "2026-07-12", "Kobal Silicon", "proj_lumenx")],
      required_relations=[],
      security_scope="perm_div_auto_confidential", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=["doc_northwind_status_2026_q2", "doc_forge2_status_2026_q2"],
      difficulty_rationale="Distractor status reports.")

_case(case_id="syn_019", question="What is the version of the Information Security Policy currently in force as of 2026-08-01?",
      question_type="single_doc_fact", difficulty="easy",
      expected_answer="v4.2 (2026 Edition), effective 2026-01-01.",
      gold_document_refs=["doc_security_policy_2026"],
      gold_source_spans=["v4.2", "2026-01-01"],
      gold_evidence_refs=[_evidence("doc_security_policy_2026", "v4.2", "2026-01-01", "v4.2", "pol_sec_2026")],
      required_relations=[],
      security_scope="perm_global_open", effective_time="2026-08-01",
      answer_policy="answer_with_citation",
      hard_negative_refs=["doc_procurement_policy", "doc_quality_policy"],
      difficulty_rationale="Time-bound 'currently in force' answer.")

_case(case_id="syn_020", question="Where was Iris Vange's field visit in May 2026, and which supplier did she review?",
      question_type="single_doc_fact", difficulty="medium",
      expected_answer="Hannover on 2026-05-04; reviewed Helion Motors.",
      gold_document_refs=["doc_iris_field_visit"],
      gold_source_spans=["Hannover", "Helion Motors"],
      gold_evidence_refs=[_evidence("doc_iris_field_visit", "v1.0", "2026-05-05", "Hannover", "sup_helion_motors")],
      required_relations=[],
      security_scope="perm_div_auto_confidential", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=[],
      difficulty_rationale="Restricted doc; location and supplier pairing.")

# ===========================================================================
# 2. CROSS-DOCUMENT MULTI-HOP (20)
# ===========================================================================

_case(case_id="syn_021",
      question="Which supplier is owned in contract by Lukas Wenger, serves the Edge Compute division, and was the subject of a March 2026 quality incident?",
      question_type="multi_hop", difficulty="hard",
      expected_answer="Kobal Silicon (contract ct_kobal_2025 v2, Lukas Wenger owner; non-conformance 2026-03-19).",
      gold_document_refs=["doc_kobal_contract", "doc_kobal_quality_incident"],
      gold_source_spans=["Kobal Silicon", "Kobal Silicon", "2026-03-19", "Kobal Silicon"],
      gold_evidence_refs=[
          _evidence("doc_kobal_contract", "v2", "2025-03-01", "Kobal Silicon", "ct_kobal_2025"),
          _evidence("doc_kobal_quality_incident", "v1.0", "2026-03-22", "2026-03-19", "sup_kobal_silicon"),
      ],
      required_relations=[
          {"kind": "contract_with_supplier", "from": "ct_kobal_2025", "to": "sup_kobal_silicon"},
          {"kind": "contract_owned_by", "from": "ct_kobal_2025", "to": "emp_lukas_wenger"},
          {"kind": "contract_serves_division", "from": "ct_kobal_2025", "to": "div_edge"},
      ],
      security_scope="perm_div_auto_confidential", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=["doc_helion_contract", "doc_polaris_contract_v2"],
      difficulty_rationale="Three-hop: contract supplier + owner + division + time-bound incident.")

_case(case_id="syn_022",
      question="Which Auroralis product was the subject of both a Q1 2026 quality audit finding and a Q2 2026 field corrective action, and who issued the corrective action bulletin?",
      question_type="multi_hop", difficulty="hard",
      expected_answer="Forge-X1 Additive Manufacturing Cell; corrective action bulletin issued by Nadya Soroka (Director, Quality & Compliance) on 2026-04-22.",
      gold_document_refs=["doc_quality_audit_2026_q1", "doc_forge_x1_recall_bulletin", "doc_forge_x1_field_log"],
      gold_source_spans=["Forge-X1", "Nadya Soroka", "12 corrective-action"],
      gold_evidence_refs=[
          _evidence("doc_quality_audit_2026_q1", "v1.0", "2026-04-30", "Forge-X1", "prod_forge_x1"),
          _evidence("doc_forge_x1_recall_bulletin", "v1.0", "2026-04-22", "Nadya Soroka", "prod_forge_x1"),
      ],
      required_relations=[
          {"kind": "event_about_product", "from": "evt_forge_x1_recall", "to": "prod_forge_x1"},
          {"kind": "event_actor", "from": "evt_forge_x1_recall", "to": "emp_nadya_soroka"},
      ],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=["doc_axis8_eol_memo"],
      difficulty_rationale="Cross-doc audit + bulletin + field log.")

_case(case_id="syn_023",
      question="Which division president also owns a supplier relationship that depends on the Polaris Steel v1 supersession event, and what was the prior contract value?",
      question_type="multi_hop", difficulty="hard",
      expected_answer="Yui Nakajima (President, Additive Manufacturing); prior Polaris Steel MSA v1 was EUR 5,100,000, superseded on 2025-09-01.",
      gold_document_refs=["doc_polaris_contract_v1", "doc_polaris_contract_v2", "doc_yui_bio"],
      gold_source_spans=["5,100,000", "5,750,000", "Yui Nakajima"],
      gold_evidence_refs=[
          _evidence("doc_polaris_contract_v1", "v1", "2024-09-01", "5,100,000", "ct_polaris_2024"),
          _evidence("doc_polaris_contract_v2", "v2", "2025-09-01", "5,750,000", "ct_polaris_2025"),
      ],
      required_relations=[
          {"kind": "contract_supersedes", "from": "ct_polaris_2025", "to": "ct_polaris_2024"},
          {"kind": "contract_serves_division", "from": "ct_polaris_2024", "to": "div_addmfg"},
          {"kind": "division_lead_employee", "from": "div_addmfg", "to": "emp_yui_nakajima"},
      ],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=["doc_helion_contract"],
      difficulty_rationale="Four-hop: contract supersession + division + president.")

_case(case_id="syn_024",
      question="Identify the product, the project that delivered it, the project sponsor, and the most recent version as of 2026-08-01.",
      question_type="multi_hop", difficulty="hard",
      expected_answer="Northwind Industrial SDK; Project Northwind (sponsor: CEO Kjartan Eliasson); v3.0.0 released 2026-01-15.",
      gold_document_refs=["doc_northwind_sdk_overview", "doc_northwind_charter"],
      gold_source_spans=["Northwind Industrial SDK", "v3.0.0", "2026-01-15", "Kjartan Eliasson"],
      gold_evidence_refs=[
          _evidence("doc_northwind_sdk_overview", "v3.0.0", "2026-01-15", "v3.0.0", "prod_northwind_sdk"),
          _evidence("doc_northwind_charter", "v1.2", "2025-09-01", "Kjartan Eliasson", "proj_northwind"),
      ],
      required_relations=[
          {"kind": "project_delivers_product", "from": "proj_northwind", "to": "prod_northwind_sdk"},
          {"kind": "project_sponsored_by", "from": "proj_northwind", "to": "ceo_kjartan_eli"},
      ],
      security_scope="perm_div_auto_confidential", effective_time="2026-08-01",
      answer_policy="answer_with_citation",
      hard_negative_refs=["doc_axis9_release_notes"],
      difficulty_rationale="Project → product → version → sponsor.")

_case(case_id="syn_025",
      question="Which Helion contract version was in force on the date of Iris Vange's Hannover visit, and what division does that contract serve?",
      question_type="multi_hop", difficulty="hard",
      expected_answer="Helion Motors MSA v3 (effective 2024-01-15 through 2027-01-14); serves Automation Systems (Iris Vange).",
      gold_document_refs=["doc_iris_field_visit", "doc_helion_contract"],
      gold_source_spans=["Hannover", "v3", "Automation Systems"],
      gold_evidence_refs=[
          _evidence("doc_iris_field_visit", "v1.0", "2026-05-05", "Hannover", "sup_helion_motors"),
          _evidence("doc_helion_contract", "v3", "2024-01-15", "v3", "ct_helion_2024"),
      ],
      required_relations=[
          {"kind": "contract_with_supplier", "from": "ct_helion_2024", "to": "sup_helion_motors"},
          {"kind": "contract_serves_division", "from": "ct_helion_2024", "to": "div_auto"},
      ],
      security_scope="perm_div_auto_confidential", effective_time="2026-05-04",
      answer_policy="answer_with_citation",
      hard_negative_refs=["doc_kobal_contract"],
      difficulty_rationale="Cross-doc time-window reasoning.")

_case(case_id="syn_026",
      question="Which corporate officer owns the Finance/Audit permission, and which restricted 2025 Q4 audit report is the only finance-restricted artifact in the corpus?",
      question_type="multi_hop", difficulty="hard",
      expected_answer="CFO Dmitri Orel; doc_audit_findings_2025_q4 is the finance-restricted audit report.",
      gold_document_refs=["doc_audit_findings_2025_q4", "doc_dmitri_bio"],
      gold_source_spans=["Finance Restricted", "Dmitri Orel"],
      gold_evidence_refs=[
          _evidence("doc_audit_findings_2025_q4", "v1.0", "2026-02-15", "Dmitri Orel", "ct_polaris_2025"),
          _evidence("doc_dmitri_bio", "v1.0", "2025-12-15", "Dmitri Orel", "emp_dmitri_orel"),
      ],
      required_relations=[
          {"kind": "employee_owns_permission", "from": "emp_dmitri_orel", "to": "perm_finance_audit"},
      ],
      security_scope="perm_finance_audit", effective_time="2026-08-03",
      answer_policy="answer_with_citation_restricted",
      hard_negative_refs=["doc_audit_findings_2026_q1"],
      difficulty_rationale="Restricted ownership + restricted content.")

_case(case_id="syn_027",
      question="Which event is recorded as occurring on 2025-09-01, and which supplier contract does it touch?",
      question_type="multi_hop", difficulty="medium",
      expected_answer="The Polaris Steel contract renewal (evt_polaris_renewal) on 2025-09-01; ct_polaris_2025 v2.",
      gold_document_refs=["doc_polaris_contract_v2", "doc_polaris_contract_v1"],
      gold_source_spans=["2025-09-01", "Superseded"],
      gold_evidence_refs=[_evidence("doc_polaris_contract_v2", "v2", "2025-09-01", "renewed", "ct_polaris_2025")],
      required_relations=[
          {"kind": "event_about_supplier", "from": "evt_polaris_renewal", "to": "sup_polaris_steel"},
      ],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=["doc_helion_contract"],
      difficulty_rationale="Distinguishing v1 (expires) from v2 (renewal).")

_case(case_id="syn_028",
      question="Which Lumen-E2 line release introduces a hardened boot chain, and who is the embedded firmware director?",
      question_type="multi_hop", difficulty="medium",
      expected_answer="Lumen-E2 v2.1.0 (released 2026-02-04); Eli Persson is the Director of Embedded Firmware.",
      gold_document_refs=["doc_lumen_e2_release_notes", "doc_eli_bio"],
      gold_source_spans=["hardened boot chain", "Eli Persson"],
      gold_evidence_refs=[_evidence("doc_lumen_e2_release_notes", "v2.1.0", "2026-02-04", "hardened boot chain", "prod_lumen_e2")],
      required_relations=[
          {"kind": "product_in_division", "from": "prod_lumen_e2", "to": "div_edge"},
      ],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=["doc_lumen_e1_eol_memo"],
      difficulty_rationale="Release + bio cross-doc.")

_case(case_id="syn_029",
      question="Which event identifies the supplier Polaris Steel as 'conditional', and what is the most recent contract effective version as of 2026-08-01?",
      question_type="multi_hop", difficulty="hard",
      expected_answer="The Q1 2026 quality audit (doc_quality_audit_2026_q1) classifies Polaris Steel as 'conditional'; the active contract is v2 (ct_polaris_2025) effective 2025-09-01.",
      gold_document_refs=["doc_quality_audit_2026_q1", "doc_polaris_contract_v2"],
      gold_source_spans=["conditional", "v2", "2025-09-01"],
      gold_evidence_refs=[
          _evidence("doc_quality_audit_2026_q1", "v1.0", "2026-04-30", "conditional", "sup_polaris_steel"),
          _evidence("doc_polaris_contract_v2", "v2", "2025-09-01", "v2", "ct_polaris_2025"),
      ],
      required_relations=[
          {"kind": "event_about_supplier", "from": "evt_polaris_renewal", "to": "sup_polaris_steel"},
      ],
      security_scope="perm_global_open", effective_time="2026-08-01",
      answer_policy="answer_with_citation",
      hard_negative_refs=["doc_helion_contract"],
      difficulty_rationale="Audit + contract version cross-doc.")

_case(case_id="syn_030",
      question="Identify the legal/privileged audit report and the General Counsel who authored it.",
      question_type="multi_hop", difficulty="medium",
      expected_answer="doc_audit_findings_2026_q1 (Legal Privileged), authored by Amani Bello.",
      gold_document_refs=["doc_audit_findings_2026_q1", "doc_amani_bio"],
      gold_source_spans=["Legal Privileged", "Amani Bello"],
      gold_evidence_refs=[_evidence("doc_audit_findings_2026_q1", "v1.0", "2026-05-10", "Amani Bello", "pol_legal_2025")],
      required_relations=[
          {"kind": "employee_owns_permission", "from": "emp_amani_bello", "to": "perm_legal_privileged"},
      ],
      security_scope="perm_legal_privileged", effective_time="2026-08-03",
      answer_policy="answer_with_citation_restricted",
      hard_negative_refs=["doc_audit_findings_2025_q4"],
      difficulty_rationale="Restricted ownership + restricted content.")

_case(case_id="syn_031",
      question="Which Auroralis division president has the most direct reports based on the org chart, and who are those direct reports?",
      question_type="multi_hop", difficulty="medium",
      expected_answer="Iris Vange (Automation Systems): Haruto Soma and Ren Kovac.",
      gold_document_refs=["doc_org_chart_2026", "doc_iris_bio", "doc_haruto_bio", "doc_ren_bio"],
      gold_source_spans=["Iris Vange", "Iris Vange", "Haruto Soma", "Ren Kovac"],
      gold_evidence_refs=[
          _evidence("doc_org_chart_2026", "v2026.Q2", "2026-04-01", "Iris Vange", "div_auto"),
          _evidence("doc_haruto_bio", "v1.0", "2025-12-15", "Iris Vange", "emp_haruto_soma"),
          _evidence("doc_ren_bio", "v1.0", "2025-12-15", "Iris Vange", "emp_ren_kovac"),
      ],
      required_relations=[
          {"kind": "employee_in_division", "from": "emp_haruto_soma", "to": "div_auto"},
          {"kind": "employee_in_division", "from": "emp_ren_kovac", "to": "div_auto"},
          {"kind": "reports_to", "from": "emp_haruto_soma", "to": "emp_iris_vange"},
          {"kind": "reports_to", "from": "emp_ren_kovac", "to": "emp_iris_vange"},
      ],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=["doc_marcus_bio"],
      difficulty_rationale="Multi-entity graph enumeration.")

_case(case_id="syn_032",
      question="Which release on 2026-02-04 was issued by an Embedded Firmware director, and which division does that director belong to?",
      question_type="multi_hop", difficulty="medium",
      expected_answer="Lumen-E2 v2.1.0 issued by Eli Persson (Edge Compute division).",
      gold_document_refs=["doc_lumen_e2_release_notes", "doc_eli_bio"],
      gold_source_spans=["2026-02-04", "Eli Persson"],
      gold_evidence_refs=[_evidence("doc_lumen_e2_release_notes", "v2.1.0", "2026-02-04", "Eli Persson", "evt_lumen_e2_release")],
      required_relations=[
          {"kind": "employee_in_division", "from": "emp_eli_persson", "to": "div_edge"},
      ],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=["doc_axis9_release_notes"],
      difficulty_rationale="Time-bounded event + division join.")

_case(case_id="syn_033",
      question="Which two events both involve the supplier Polaris Steel, and on which dates did they occur?",
      question_type="multi_hop", difficulty="hard",
      expected_answer="evt_polaris_renewal on 2025-09-01; the v1 contract expiry is implied 2025-08-31 (no event record).",
      gold_document_refs=["doc_polaris_contract_v2", "doc_polaris_contract_v1"],
      gold_source_spans=["2025-09-01", "2025-08-31"],
      gold_evidence_refs=[_evidence("doc_polaris_contract_v2", "v2", "2025-09-01", "2025-09-01", "ct_polaris_2025")],
      required_relations=[
          {"kind": "event_about_supplier", "from": "evt_polaris_renewal", "to": "sup_polaris_steel"},
      ],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=["doc_helion_contract"],
      difficulty_rationale="Event timeline enumeration; trap: only one event is recorded in the world model.")

_case(case_id="syn_034",
      question="Which CEO biography mentions the internal codename 'Project Northwind'?",
      question_type="multi_hop", difficulty="medium",
      expected_answer="doc_ceo_bio (Kjartan Eliasson - CEO Biography) and the org chart via the company record (internal_codename=Project Northwind).",
      gold_document_refs=["doc_ceo_bio", "doc_org_chart_2026"],
      gold_source_spans=["Kjartan Eliasson", "Automation Systems"],
      gold_evidence_refs=[_evidence("doc_ceo_bio", "v1.0", "2025-12-15", "Kjartan Eliasson", "ceo_kjartan_eli")],
      required_relations=[],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=["doc_yui_bio"],
      difficulty_rationale="Note: codename is on the company record, not on the CEO biography — must answer carefully.")

_case(case_id="syn_035",
      question="Identify the Q1 2026 audit report that references the Polaris Steel v2 contract variance vs forecast.",
      question_type="multi_hop", difficulty="medium",
      expected_answer="doc_audit_findings_2025_q4 (Finance Restricted), prepared by Dmitri Orel.",
      gold_document_refs=["doc_audit_findings_2025_q4", "doc_polaris_contract_v2"],
      gold_source_spans=["Polaris Steel v2 contract variance", "5,750,000"],
      gold_evidence_refs=[_evidence("doc_audit_findings_2025_q4", "v1.0", "2026-02-15", "Polaris Steel", "ct_polaris_2025")],
      required_relations=[
          {"kind": "employee_owns_permission", "from": "emp_dmitri_orel", "to": "perm_finance_audit"},
      ],
      security_scope="perm_finance_audit", effective_time="2026-08-03",
      answer_policy="answer_with_citation_restricted",
      hard_negative_refs=["doc_audit_findings_2026_q1"],
      difficulty_rationale="Restricted ownership + time confusion (Q1 2026 vs Q4 2025 report).")

_case(case_id="syn_036",
      question="Which project was reported at status 'on_track' in Q2 2026 status reports, and what budget does it carry?",
      question_type="multi_hop", difficulty="hard",
      expected_answer="Project Forge-II (proj_forge2): EUR 9,800,000; on_track per doc_forge2_status_2026_q2.",
      gold_document_refs=["doc_forge2_charter", "doc_forge2_status_2026_q2"],
      gold_source_spans=["9,800,000", "Powder feed corrective action"],
      gold_evidence_refs=[
          _evidence("doc_forge2_charter", "v1.1", "2025-11-01", "9,800,000", "proj_forge2"),
          _evidence("doc_forge2_status_2026_q2", "v1.0", "2026-07-10", "on_track", "proj_forge2"),
      ],
      required_relations=[
          {"kind": "project_owned_by_division", "from": "proj_forge2", "to": "div_addmfg"},
      ],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=["doc_northwind_status_2026_q2", "doc_lumenx_status_2026_q2"],
      difficulty_rationale="Distractor is Lumen-X 'at_risk'.")

_case(case_id="syn_037",
      question="Which employee is both a member of the legal privilege list and the document owner of the Export Control policy?",
      question_type="multi_hop", difficulty="hard",
      expected_answer="Amani Bello (General Counsel).",
      gold_document_refs=["doc_export_policy", "doc_audit_findings_2026_q1"],
      gold_source_spans=["Amani Bello", "legal"],
      gold_evidence_refs=[_evidence("doc_export_policy", "v1.5", "2025-02-01", "Amani Bello", "emp_amani_bello")],
      required_relations=[
          {"kind": "employee_owns_permission", "from": "emp_amani_bello", "to": "perm_legal_privileged"},
      ],
      security_scope="perm_legal_privileged", effective_time="2026-08-03",
      answer_policy="answer_with_citation_restricted",
      hard_negative_refs=["doc_priya_bio"],
      difficulty_rationale="Membership intersection across permission + ownership.")

_case(case_id="syn_038",
      question="Trace the chain: which Quality director signed the 2026-04-22 corrective action bulletin, and which incident report references the same root cause?",
      question_type="multi_hop", difficulty="hard",
      expected_answer="Nadya Soroka signed the Forge-X1 corrective action; related: doc_kobal_quality_incident is a separate incident but authored by the same director.",
      gold_document_refs=["doc_forge_x1_recall_bulletin", "doc_kobal_quality_incident"],
      gold_source_spans=["Nadya Soroka", "2026-03-19", "Kobal Silicon"],
      gold_evidence_refs=[
          _evidence("doc_forge_x1_recall_bulletin", "v1.0", "2026-04-22", "Nadya Soroka", "prod_forge_x1"),
          _evidence("doc_kobal_quality_incident", "v1.0", "2026-03-22", "Nadya Soroka", "sup_kobal_silicon"),
      ],
      required_relations=[
          {"kind": "event_actor", "from": "evt_forge_x1_recall", "to": "emp_nadya_soroka"},
      ],
      security_scope="perm_div_auto_confidential", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=[],
      difficulty_rationale="Cross-incident tracing with shared actor.")

_case(case_id="syn_039",
      question="Which Steering Committee meeting minutes record the Axis-9 integration milestone, and which CEO chairs that committee?",
      question_type="multi_hop", difficulty="medium",
      expected_answer="doc_northwind_meeting_minutes (2026-06-15); Kjartan Eliasson chairs.",
      gold_document_refs=["doc_northwind_meeting_minutes", "doc_ceo_bio"],
      gold_source_spans=["Axis-9", "Kjartan Eliasson"],
      gold_evidence_refs=[_evidence("doc_northwind_meeting_minutes", "v1.0", "2026-06-16", "Kjartan Eliasson", "proj_northwind")],
      required_relations=[
          {"kind": "project_sponsored_by", "from": "proj_northwind", "to": "ceo_kjartan_eli"},
      ],
      security_scope="perm_div_auto_confidential", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=[],
      difficulty_rationale="Restricted doc; meeting + chair.")

_case(case_id="syn_040",
      question="Identify the latest Auroralis company calendar event list and the three product release dates it lists.",
      question_type="multi_hop", difficulty="medium",
      expected_answer="doc_corp_calendar_2026 lists: Axis-9 v9.4.0 (2025-11-12), Lumen-E2 v2.1.0 (2026-02-04), Northwind SDK v3.0.0 (2026-01-15).",
      gold_document_refs=["doc_corp_calendar_2026", "doc_axis9_release_notes", "doc_lumen_e2_release_notes", "doc_northwind_sdk_overview"],
      gold_source_spans=["Axis-9 v9.4.0", "v9.4.0", "v2.1.0", "v3.0.0"],
      gold_evidence_refs=[_evidence("doc_corp_calendar_2026", "v1.0", "2026-01-01", "v9.4.0", "company")],
      required_relations=[],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=[],
      difficulty_rationale="Multi-entity cross-reference inside calendar.")

# ===========================================================================
# 3. GRAPH (RELATIONS / PATH / COMMUNITY) (15)
# ===========================================================================

_case(case_id="syn_041",
      question="Walk the graph: from supplier Polaris Steel → contract → division → division president. Identify the president.",
      question_type="graph_path", difficulty="medium",
      expected_answer="Polaris Steel → ct_polaris_2025 → div_addmfg → Yui Nakajima.",
      gold_document_refs=["doc_polaris_contract_v2", "doc_yui_bio"],
      gold_source_spans=["Polaris Steel", "Yui Nakajima"],
      gold_evidence_refs=[_evidence("doc_polaris_contract_v2", "v2", "2025-09-01", "Additive Manufacturing", "ct_polaris_2025")],
      required_relations=[
          {"kind": "contract_with_supplier", "from": "ct_polaris_2025", "to": "sup_polaris_steel"},
          {"kind": "contract_serves_division", "from": "ct_polaris_2025", "to": "div_addmfg"},
          {"kind": "division_lead_employee", "from": "div_addmfg", "to": "emp_yui_nakajima"},
      ],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=["doc_helion_contract"],
      difficulty_rationale="Three-edge graph walk.")

_case(case_id="syn_042",
      question="Walk the graph: product Axis-9 → division → president → sponsor of which project?",
      question_type="graph_path", difficulty="hard",
      expected_answer="prod_axis_9 → div_auto → Iris Vange → proj_northwind (sponsor: Kjartan Eliasson, NOT Iris Vange).",
      gold_document_refs=["doc_org_chart_2026", "doc_northwind_charter", "doc_iris_bio"],
      gold_source_spans=["Automation Systems", "Project Northwind", "Iris Vange"],
      gold_evidence_refs=[
          _evidence("doc_org_chart_2026", "v2026.Q2", "2026-04-01", "Iris Vange", "div_auto"),
          _evidence("doc_northwind_charter", "v1.2", "2025-09-01", "Project Northwind", "proj_northwind"),
      ],
      required_relations=[
          {"kind": "product_in_division", "from": "prod_axis_9", "to": "div_auto"},
          {"kind": "division_lead_employee", "from": "div_auto", "to": "emp_iris_vange"},
          {"kind": "project_owned_by_division", "from": "proj_northwind", "to": "div_auto"},
          {"kind": "project_sponsored_by", "from": "proj_northwind", "to": "ceo_kjartan_eli"},
      ],
      security_scope="perm_div_auto_confidential", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=[],
      difficulty_rationale="Trap: division president ≠ project sponsor for Northwind.")

_case(case_id="syn_043",
      question="Find the policy owner of the 2026 Information Security Policy and the permission scope they own.",
      question_type="graph_relation", difficulty="medium",
      expected_answer="Priya Kaur (CISO) owns pol_sec_2026; she is also a member of perm_finance_audit (alongside CFO Dmitri Orel).",
      gold_document_refs=["doc_security_policy_2026", "doc_priya_bio"],
      gold_source_spans=["Priya Kaur", "Priya Kaur"],
      gold_evidence_refs=[_evidence("doc_security_policy_2026", "v4.2", "2026-01-01", "Priya Kaur", "emp_priya_kaur")],
      required_relations=[
          {"kind": "policy_owned_by", "from": "pol_sec_2026", "to": "emp_priya_kaur"},
          {"kind": "employee_owns_permission", "from": "emp_priya_kaur", "to": "perm_finance_audit"},
      ],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=["doc_amani_bio"],
      difficulty_rationale="Policy ownership + permission membership look-up.")

_case(case_id="syn_044",
      question="Walk the graph: from event evt_forge_x1_recall → product → division → president.",
      question_type="graph_path", difficulty="medium",
      expected_answer="Forge-X1 corrective action (2026-04-22) → prod_forge_x1 → div_addmfg → Yui Nakajima.",
      gold_document_refs=["doc_forge_x1_recall_bulletin", "doc_yui_bio"],
      gold_source_spans=["Forge-X1", "Yui Nakajima"],
      gold_evidence_refs=[_evidence("doc_forge_x1_recall_bulletin", "v1.0", "2026-04-22", "powder feed", "prod_forge_x1")],
      required_relations=[
          {"kind": "event_about_product", "from": "evt_forge_x1_recall", "to": "prod_forge_x1"},
          {"kind": "product_in_division", "from": "prod_forge_x1", "to": "div_addmfg"},
          {"kind": "division_lead_employee", "from": "div_addmfg", "to": "emp_yui_nakajima"},
      ],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=[],
      difficulty_rationale="Three-edge path traversal.")

_case(case_id="syn_045",
      question="Find the contract superedge between Polaris v1 and v2, and identify the supersession event date.",
      question_type="graph_relation", difficulty="medium",
      expected_answer="ct_polaris_2025 supersedes ct_polaris_2024; evt_polaris_renewal on 2025-09-01.",
      gold_document_refs=["doc_polaris_contract_v1", "doc_polaris_contract_v2"],
      gold_source_spans=["Superseded by", "2025-09-01"],
      gold_evidence_refs=[_evidence("doc_polaris_contract_v2", "v2", "2025-09-01", "Supersedes", "ct_polaris_2025")],
      required_relations=[
          {"kind": "contract_supersedes", "from": "ct_polaris_2025", "to": "ct_polaris_2024"},
          {"kind": "event_about_supplier", "from": "evt_polaris_renewal", "to": "sup_polaris_steel"},
      ],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=[],
      difficulty_rationale="Graph relation with timestamp.")

_case(case_id="syn_046",
      question="Which division has the most contracts (as serving division) recorded in the world model, and how many?",
      question_type="graph_community", difficulty="hard",
      expected_answer="div_auto: 1 (Helion); div_edge: 1 (Kobal); div_addmfg: 2 (Polaris v1 and v2); div_corp: 1 (Meridian). Additive Manufacturing leads with 2.",
      gold_document_refs=["doc_polaris_contract_v1", "doc_polaris_contract_v2", "doc_helion_contract", "doc_kobal_contract", "doc_meridian_contract"],
      gold_source_spans=["Polaris Steel", "Additive Manufacturing", "Automation Systems", "Edge Compute", "Meridian"],
      gold_evidence_refs=[_evidence("doc_polaris_contract_v2", "v2", "2025-09-01", "Additive Manufacturing", "ct_polaris_2025")],
      required_relations=[
          {"kind": "contract_serves_division", "from": "ct_polaris_2025", "to": "div_addmfg"},
          {"kind": "contract_serves_division", "from": "ct_polaris_2024", "to": "div_addmfg"},
      ],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=[],
      difficulty_rationale="Aggregation over graph edges.")

_case(case_id="syn_047",
      question="Walk the graph: permission perm_div_auto_confidential → owner → division president → product.",
      question_type="graph_path", difficulty="hard",
      expected_answer="perm_div_auto_confidential → emp_iris_vange → prod_axis_9 (and prod_axis_8, prod_northwind_sdk).",
      gold_document_refs=["doc_iris_bio", "doc_axis9_release_notes"],
      gold_source_spans=["Iris Vange", "Axis-9"],
      gold_evidence_refs=[_evidence("doc_iris_bio", "v1.0", "2025-12-15", "Iris Vange", "emp_iris_vange")],
      required_relations=[
          {"kind": "employee_owns_permission", "from": "emp_iris_vange", "to": "perm_div_auto_confidential"},
          {"kind": "division_lead_employee", "from": "div_auto", "to": "emp_iris_vange"},
          {"kind": "product_in_division", "from": "prod_axis_9", "to": "div_auto"},
      ],
      security_scope="perm_div_auto_confidential", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=[],
      difficulty_rationale="Permission → owner → division → products.")

_case(case_id="syn_048",
      question="Which event actor is also a division president, and which event did they act on?",
      question_type="graph_relation", difficulty="hard",
      expected_answer="Iris Vange (President, Automation Systems) acted on evt_axis_8_eol (2026-03-01).",
      gold_document_refs=["doc_axis8_eol_memo", "doc_iris_bio"],
      gold_source_spans=["Iris Vange", "Iris Vange"],
      gold_evidence_refs=[_evidence("doc_axis8_eol_memo", "v1.0", "2026-03-01", "Iris Vange", "prod_axis_8")],
      required_relations=[
          {"kind": "event_actor", "from": "evt_axis_8_eol", "to": "emp_iris_vange"},
          {"kind": "division_lead_employee", "from": "div_auto", "to": "emp_iris_vange"},
      ],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=[],
      difficulty_rationale="Actor + role intersection.")

_case(case_id="syn_049",
      question="Identify the policy supersession edge in the world model and its direction.",
      question_type="graph_relation", difficulty="easy",
      expected_answer="pol_sec_2026 supersedes pol_sec_2024 (direction: 2026 -> 2024).",
      gold_document_refs=["doc_security_policy_2026", "doc_security_policy_2024"],
      gold_source_spans=["Supersedes", "v4.1"],
      gold_evidence_refs=[_evidence("doc_security_policy_2026", "v4.2", "2026-01-01", "Supersedes", "pol_sec_2026")],
      required_relations=[
          {"kind": "policy_supersedes", "from": "pol_sec_2026", "to": "pol_sec_2024"},
          {"kind": "policy_owned_by", "from": "pol_sec_2026", "to": "emp_priya_kaur"},
      ],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=[],
      difficulty_rationale="Direct relation extraction.")

_case(case_id="syn_050",
      question="Walk the graph from project proj_lumenx → division → president → reports-to chain (2 hops).",
      question_type="graph_path", difficulty="medium",
      expected_answer="proj_lumenx → div_edge → Marcus Tien → reports to Kjartan Eliasson.",
      gold_document_refs=["doc_lumenx_charter", "doc_marcus_bio", "doc_ceo_bio", "doc_org_chart_2026"],
      gold_source_spans=["Marcus Tien", "Marcus Tien", "Kjartan Eliasson", "Marcus Tien"],
      gold_evidence_refs=[_evidence("doc_lumenx_charter", "v1.0", "2026-01-15", "Marcus Tien", "proj_lumenx")],
      required_relations=[
          {"kind": "project_owned_by_division", "from": "proj_lumenx", "to": "div_edge"},
          {"kind": "division_lead_employee", "from": "div_edge", "to": "emp_marcus_tien"},
          {"kind": "reports_to", "from": "emp_marcus_tien", "to": "ceo_kjartan_eli"},
      ],
      security_scope="perm_div_auto_confidential", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=[],
      difficulty_rationale="Project → division → president → CEO chain.")

_case(case_id="syn_051",
      question="Compute the simple community: employees who are direct reports of Solveig Hagen.",
      question_type="graph_community", difficulty="medium",
      expected_answer="Lukas Wenger (Head of Procurement), Nadya Soroka (Director, Quality & Compliance).",
      gold_document_refs=["doc_org_chart_2026"],
      gold_source_spans=["Lukas Wenger", "Nadya Soroka", "Solveig Hagen"],
      gold_evidence_refs=[
          _evidence("doc_org_chart_2026", "v2026.Q2", "2026-04-01", "Solveig Hagen", "emp_solveig_hagen"),
          _evidence("doc_lukas_bio", "v1.0", "2025-12-15", "Solveig Hagen", "emp_lukas_wenger"),
          _evidence("doc_nadya_bio", "v1.0", "2025-12-15", "Solveig Hagen", "emp_nadya_soroka"),
      ],
      required_relations=[
          {"kind": "reports_to", "from": "emp_lukas_wenger", "to": "emp_solveig_hagen"},
          {"kind": "reports_to", "from": "emp_nadya_soroka", "to": "emp_solveig_hagen"},
      ],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=[],
      difficulty_rationale="Community detection by manager.")

_case(case_id="syn_052",
      question="Which two events are linked to the 2026 Information Security Policy, and on what dates?",
      question_type="graph_relation", difficulty="medium",
      expected_answer="evt_policy_2026 (policy_publication) on 2026-01-01.",
      gold_document_refs=["doc_security_policy_2026", "doc_security_policy_2024"],
      gold_source_spans=["2026-01-01", "2024-01-01"],
      gold_evidence_refs=[_evidence("doc_security_policy_2026", "v4.2", "2026-01-01", "2026-01-01", "pol_sec_2026")],
      required_relations=[
          {"kind": "event_about_policy", "from": "evt_policy_2026", "to": "pol_sec_2026"},
          {"kind": "policy_supersedes", "from": "pol_sec_2026", "to": "pol_sec_2024"},
      ],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=[],
      difficulty_rationale="Trap: only one event is recorded for this policy.")

_case(case_id="syn_053",
      question="Walk the graph: product prod_northwind_sdk → project → sponsor.",
      question_type="graph_path", difficulty="easy",
      expected_answer="prod_northwind_sdk → proj_northwind → Kjartan Eliasson (CEO sponsor).",
      gold_document_refs=["doc_northwind_sdk_overview", "doc_northwind_charter"],
      gold_source_spans=["Project Northwind", "Kjartan Eliasson"],
      gold_evidence_refs=[
          _evidence("doc_northwind_sdk_overview", "v3.0.0", "2026-01-15", "Project Northwind", "prod_northwind_sdk"),
          _evidence("doc_northwind_charter", "v1.2", "2025-09-01", "Kjartan Eliasson", "proj_northwind"),
      ],
      required_relations=[
          {"kind": "project_delivers_product", "from": "proj_northwind", "to": "prod_northwind_sdk"},
          {"kind": "project_sponsored_by", "from": "proj_northwind", "to": "ceo_kjartan_eli"},
      ],
      security_scope="perm_div_auto_confidential", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=[],
      difficulty_rationale="Product → project → sponsor path.")

_case(case_id="syn_054",
      question="Which two products are owned by the same director?",
      question_type="graph_relation", difficulty="medium",
      expected_answer="Haruto Soma owns prod_axis_9 and prod_northwind_sdk.",
      gold_document_refs=["doc_axis9_release_notes", "doc_northwind_sdk_overview", "doc_haruto_bio", "doc_org_chart_2026"],
      gold_source_spans=["Haruto Soma", "Haruto Soma", "Haruto Soma", "Automation Systems"],
      gold_evidence_refs=[
          _evidence("doc_axis9_release_notes", "v9.4.0", "2025-11-12", "Haruto Soma", "prod_axis_9"),
          _evidence("doc_northwind_sdk_overview", "v3.0.0", "2026-01-15", "Haruto Soma", "prod_northwind_sdk"),
      ],
      required_relations=[
          {"kind": "product_owner", "from": "prod_axis_9", "to": "emp_haruto_soma"},
          {"kind": "product_owner", "from": "prod_northwind_sdk", "to": "emp_haruto_soma"},
      ],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=[],
      difficulty_rationale="Identify shared owner across products.")

_case(case_id="syn_055",
      question="Identify the contract owner who owns every contract in the corpus.",
      question_type="graph_community", difficulty="easy",
      expected_answer="Lukas Wenger (Head of Procurement) owns every contract: Helion, Kobal, Meridian, Polaris v1, Polaris v2.",
      gold_document_refs=["doc_lukas_bio", "doc_helion_contract", "doc_kobal_contract", "doc_meridian_contract", "doc_polaris_contract_v1", "doc_polaris_contract_v2"],
      gold_source_spans=["Lukas Wenger", "Lukas Wenger", "Lukas Wenger", "Lukas Wenger", "Lukas Wenger", "Lukas Wenger"],
      gold_evidence_refs=[_evidence("doc_lukas_bio", "v1.0", "2025-12-15", "Lukas Wenger", "emp_lukas_wenger")],
      required_relations=[
          {"kind": "contract_owned_by", "from": "ct_helion_2024", "to": "emp_lukas_wenger"},
          {"kind": "contract_owned_by", "from": "ct_kobal_2025", "to": "emp_lukas_wenger"},
          {"kind": "contract_owned_by", "from": "ct_meridian_2025", "to": "emp_lukas_wenger"},
          {"kind": "contract_owned_by", "from": "ct_polaris_2024", "to": "emp_lukas_wenger"},
          {"kind": "contract_owned_by", "from": "ct_polaris_2025", "to": "emp_lukas_wenger"},
      ],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=[],
      difficulty_rationale="Hub identification across all contract edges.")

# ===========================================================================
# 4. VERSION / TIME / CONFLICT (10)
# ===========================================================================

_case(case_id="syn_056",
      question="What version of the Information Security Policy was in force on 2024-06-15, and what version replaced it on 2026-01-01?",
      question_type="temporal_version", difficulty="medium",
      expected_answer="v4.1 (2024 Edition) on 2024-06-15; superseded by v4.2 (2026 Edition) on 2026-01-01.",
      gold_document_refs=["doc_security_policy_2024", "doc_security_policy_2026"],
      gold_source_spans=["v4.1", "v4.2", "2024-01-01", "2026-01-01"],
      gold_evidence_refs=[
          _evidence("doc_security_policy_2024", "v4.1", "2024-01-01", "v4.1", "pol_sec_2024"),
          _evidence("doc_security_policy_2026", "v4.2", "2026-01-01", "v4.2", "pol_sec_2026"),
      ],
      required_relations=[
          {"kind": "policy_supersedes", "from": "pol_sec_2026", "to": "pol_sec_2024"},
      ],
      security_scope="perm_global_open", effective_time="2024-06-15",
      answer_policy="answer_with_citation",
      hard_negative_refs=[],
      difficulty_rationale="Two time points, two versions.")

_case(case_id="syn_057",
      question="Was the Polaris Steel MSA v1 (EUR 5,100,000) in force on 2025-09-01, or had it been superseded?",
      question_type="temporal_conflict", difficulty="medium",
      expected_answer="Superseded on 2025-09-01 by ct_polaris_2025 v2 (EUR 5,750,000); v1 expired 2025-08-31.",
      gold_document_refs=["doc_polaris_contract_v1", "doc_polaris_contract_v2"],
      gold_source_spans=["2025-08-31", "2025-09-01", "Superseded"],
      gold_evidence_refs=[
          _evidence("doc_polaris_contract_v1", "v1", "2024-09-01", "2025-08-31", "ct_polaris_2024"),
          _evidence("doc_polaris_contract_v2", "v2", "2025-09-01", "2025-09-01", "ct_polaris_2025"),
      ],
      required_relations=[
          {"kind": "contract_supersedes", "from": "ct_polaris_2025", "to": "ct_polaris_2024"},
      ],
      security_scope="perm_global_open", effective_time="2025-09-01",
      answer_policy="answer_with_citation",
      hard_negative_refs=[],
      difficulty_rationale="Day-of supersession boundary.")

_case(case_id="syn_058",
      question="On 2026-01-15, which product release was effective?",
      question_type="temporal_version", difficulty="easy",
      expected_answer="Northwind Industrial SDK v3.0.0, effective 2026-01-15 (Haruto Soma).",
      gold_document_refs=["doc_northwind_sdk_overview"],
      gold_source_spans=["v3.0.0", "2026-01-15"],
      gold_evidence_refs=[_evidence("doc_northwind_sdk_overview", "v3.0.0", "2026-01-15", "v3.0.0", "prod_northwind_sdk")],
      required_relations=[],
      security_scope="perm_global_open", effective_time="2026-01-15",
      answer_policy="answer_with_citation",
      hard_negative_refs=["doc_axis9_release_notes", "doc_lumen_e2_release_notes"],
      difficulty_rationale="Exact date pinning.")

_case(case_id="syn_059",
      question="Was the Lumen-E2 v2.1.0 release effective on 2026-01-15?",
      question_type="temporal_conflict", difficulty="easy",
      expected_answer="No. Lumen-E2 v2.1.0 was released on 2026-02-04.",
      gold_document_refs=["doc_lumen_e2_release_notes"],
      gold_source_spans=["2026-02-04"],
      gold_evidence_refs=[_evidence("doc_lumen_e2_release_notes", "v2.1.0", "2026-02-04", "2026-02-04", "prod_lumen_e2")],
      required_relations=[],
      security_scope="perm_global_open", effective_time="2026-01-15",
      answer_policy="answer_with_citation",
      hard_negative_refs=[],
      difficulty_rationale="Negative answer with effective-time refutation.")

_case(case_id="syn_060",
      question="Which Polaris contract version is in force as of 2026-08-01, and which was in force on 2024-12-15?",
      question_type="temporal_version", difficulty="hard",
      expected_answer="ct_polaris_2025 v2 as of 2026-08-01; ct_polaris_2024 v1 on 2024-12-15.",
      gold_document_refs=["doc_polaris_contract_v1", "doc_polaris_contract_v2"],
      gold_source_spans=["2024-09-01", "2025-09-01"],
      gold_evidence_refs=[
          _evidence("doc_polaris_contract_v1", "v1", "2024-09-01", "2025-08-31", "ct_polaris_2024"),
          _evidence("doc_polaris_contract_v2", "v2", "2025-09-01", "2027-08-31", "ct_polaris_2025"),
      ],
      required_relations=[
          {"kind": "contract_supersedes", "from": "ct_polaris_2025", "to": "ct_polaris_2024"},
      ],
      security_scope="perm_global_open", effective_time="2024-12-15",
      answer_policy="answer_with_citation",
      hard_negative_refs=[],
      difficulty_rationale="Two time points across supersession boundary.")

_case(case_id="syn_061",
      question="Did Iris Vange sign off on the Axis-9 v9.4.0 release?",
      question_type="temporal_conflict", difficulty="easy",
      expected_answer="No. Axis-9 v9.4.0 was released by Haruto Soma on 2025-11-12.",
      gold_document_refs=["doc_axis9_release_notes"],
      gold_source_spans=["Haruto Soma", "2025-11-12"],
      gold_evidence_refs=[_evidence("doc_axis9_release_notes", "v9.4.0", "2025-11-12", "Haruto Soma", "evt_axis_9_release")],
      required_relations=[],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=["doc_axis8_eol_memo"],
      difficulty_rationale="Actor disambiguation; Iris Vange signed the Axis-8 EOL memo, not Axis-9.")

_case(case_id="syn_062",
      question="Which corporate calendar lists three product release dates, and what are they?",
      question_type="temporal_version", difficulty="medium",
      expected_answer="doc_corp_calendar_2026: Axis-9 v9.4.0 (2025-11-12), Lumen-E2 v2.1.0 (2026-02-04), Northwind SDK v3.0.0 (2026-01-15).",
      gold_document_refs=["doc_corp_calendar_2026"],
      gold_source_spans=["Axis-9 v9.4.0", "Lumen-E2 v2.1.0", "Northwind SDK v3.0.0"],
      gold_evidence_refs=[_evidence("doc_corp_calendar_2026", "v1.0", "2026-01-01", "v9.4.0", "company")],
      required_relations=[],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=[],
      difficulty_rationale="Calendar enumeration.")

_case(case_id="syn_063",
      question="Was the Information Security Policy 2024 Edition in force on 2026-02-01?",
      question_type="temporal_conflict", difficulty="easy",
      expected_answer="No. The 2026 Edition (v4.2) superseded it on 2026-01-01.",
      gold_document_refs=["doc_security_policy_2024", "doc_security_policy_2026"],
      gold_source_spans=["v4.1", "v4.2"],
      gold_evidence_refs=[_evidence("doc_security_policy_2026", "v4.2", "2026-01-01", "2026-01-01", "pol_sec_2026")],
      required_relations=[
          {"kind": "policy_supersedes", "from": "pol_sec_2026", "to": "pol_sec_2024"},
      ],
      security_scope="perm_global_open", effective_time="2026-02-01",
      answer_policy="answer_with_citation",
      hard_negative_refs=[],
      difficulty_rationale="Post-supersession negative.")

_case(case_id="syn_064",
      question="Identify the contract effective date when Lukas Wenger took over ownership of the v2 Polaris Steel MSA.",
      question_type="temporal_version", difficulty="easy",
      expected_answer="ct_polaris_2025 v2, effective 2025-09-01.",
      gold_document_refs=["doc_polaris_contract_v2"],
      gold_source_spans=["2025-09-01", "v2"],
      gold_evidence_refs=[_evidence("doc_polaris_contract_v2", "v2", "2025-09-01", "2025-09-01", "ct_polaris_2025")],
      required_relations=[],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=["doc_axis9_release_notes"],
      difficulty_rationale="Disambiguate from v1.")

_case(case_id="syn_065",
      question="Which event is recorded on 2025-11-12 and which product version did it introduce?",
      question_type="temporal_version", difficulty="easy",
      expected_answer="evt_axis_9_release (2025-11-12); introduced prod_axis_9 v9.4.0.",
      gold_document_refs=["doc_axis9_release_notes"],
      gold_source_spans=["2025-11-12", "v9.4.0"],
      gold_evidence_refs=[_evidence("doc_axis9_release_notes", "v9.4.0", "2025-11-12", "2025-11-12", "evt_axis_9_release")],
      required_relations=[
          {"kind": "event_about_product", "from": "evt_axis_9_release", "to": "prod_axis_9"},
      ],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="answer_with_citation",
      hard_negative_refs=[],
      difficulty_rationale="Event + version binding.")

# ===========================================================================
# 5. NO-ANSWER / ABSTAIN (5)
# ===========================================================================

_case(case_id="syn_066",
      question="Who is Auroralis's Chief Marketing Officer?",
      question_type="no_answer", difficulty="easy",
      expected_outcome="abstain",
      expected_answer="(no answer)",
      gold_document_refs=[],
      gold_source_spans=[],
      gold_evidence_refs=[],
      required_relations=[],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="must_abstain",
      hard_negative_refs=["doc_org_chart_2026"],
      difficulty_rationale="Auroralis has no CMO in the world model.")

_case(case_id="syn_067",
      question="What is Auroralis's revenue for fiscal year 2025?",
      question_type="no_answer", difficulty="easy",
      expected_outcome="abstain",
      expected_answer="(no answer)",
      gold_document_refs=[],
      gold_source_spans=[],
      gold_evidence_refs=[],
      required_relations=[],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="must_abstain",
      hard_negative_refs=["doc_dmitri_bio"],
      difficulty_rationale="No revenue record in the world model.")

_case(case_id="syn_068",
      question="What is the SHA-256 of the Axis-9 v9.4.0 firmware image?",
      question_type="no_answer", difficulty="medium",
      expected_outcome="abstain",
      expected_answer="(no answer)",
      gold_document_refs=[],
      gold_source_spans=[],
      gold_evidence_refs=[],
      required_relations=[],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="must_abstain",
      hard_negative_refs=["doc_axis9_release_notes"],
      difficulty_rationale="No firmware hash in corpus.")

_case(case_id="syn_069",
      question="Which country does Helion Motors' main factory reside in?",
      question_type="no_answer", difficulty="medium",
      expected_outcome="abstain",
      expected_answer="(no answer)",
      gold_document_refs=[],
      gold_source_spans=[],
      gold_evidence_refs=[],
      required_relations=[],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="must_abstain",
      hard_negative_refs=["doc_supplier_brief_sup_helion_motors"],
      difficulty_rationale="Country HQ is named in supplier brief (Germany) but the question asks about main factory — corpus never identifies a factory location.")

_case(case_id="syn_070",
      question="What is the salary of Iris Vange?",
      question_type="no_answer", difficulty="easy",
      expected_outcome="abstain",
      expected_answer="(no answer)",
      gold_document_refs=[],
      gold_source_spans=[],
      gold_evidence_refs=[],
      required_relations=[],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="must_abstain",
      hard_negative_refs=["doc_iris_bio", "doc_iris_field_visit"],
      difficulty_rationale="No compensation data in corpus.")

# ===========================================================================
# 6. PERMISSION / SENSITIVE (5)
# ===========================================================================

_case(case_id="syn_071",
      question="Summarize the contents of the 2026 Q1 internal audit findings.",
      question_type="permission_restricted", difficulty="medium",
      expected_outcome="restricted_answer",
      expected_answer="Restricted: permitted principals are Amani Bello and CEO Kjartan Eliasson. Surface only: doc_audit_findings_2026_q1 is legal-privileged work product on export-control screening for the Lumen-E2 line. Refuse to disclose detailed findings to non-privileged callers.",
      gold_document_refs=["doc_audit_findings_2026_q1"],
      gold_source_spans=["Legal Privileged", "Amani Bello", "Kjartan Eliasson"],
      gold_evidence_refs=[_evidence("doc_audit_findings_2026_q1", "v1.0", "2026-05-10", "Legal Privileged", "pol_legal_2025")],
      required_relations=[
          {"kind": "employee_owns_permission", "from": "emp_amani_bello", "to": "perm_legal_privileged"},
      ],
      security_scope="perm_legal_privileged", effective_time="2026-08-03",
      answer_policy="restricted_or_deny",
      hard_negative_refs=["doc_audit_findings_2025_q4"],
      difficulty_rationale="Legal privileged; must restrict or deny.")

_case(case_id="syn_072",
      question="Summarize the contents of the 2025 Q4 finance-restricted audit findings.",
      question_type="permission_restricted", difficulty="medium",
      expected_outcome="restricted_answer",
      expected_answer="Restricted: permitted principals are Dmitri Orel (CFO) and Priya Kaur (CISO). Surface only: doc_audit_findings_2025_q4 reviews Polaris Steel v2 contract variance vs forecast. Refuse to disclose detailed variance figures to non-finance callers.",
      gold_document_refs=["doc_audit_findings_2025_q4"],
      gold_source_spans=["Finance Restricted", "Dmitri Orel"],
      gold_evidence_refs=[_evidence("doc_audit_findings_2025_q4", "v1.0", "2026-02-15", "Finance Restricted", "ct_polaris_2025")],
      required_relations=[
          {"kind": "employee_owns_permission", "from": "emp_dmitri_orel", "to": "perm_finance_audit"},
      ],
      security_scope="perm_finance_audit", effective_time="2026-08-03",
      answer_policy="restricted_or_deny",
      hard_negative_refs=["doc_audit_findings_2026_q1"],
      difficulty_rationale="Finance restricted; must restrict or deny.")

_case(case_id="syn_073",
      question="Reveal the contents of the Helion Motors MSA contract summary (v3).",
      question_type="permission_restricted", difficulty="medium",
      expected_outcome="restricted_answer",
      expected_answer="Restricted to perm_div_auto_confidential. Surface only to Automation Systems division: doc_helion_contract (v3, effective 2024-01-15 through 2027-01-14, EUR 12,500,000, owner Lukas Wenger). Deny to non-division callers.",
      gold_document_refs=["doc_helion_contract"],
      gold_source_spans=["Automation Systems", "Helion Motors", "v3"],
      gold_evidence_refs=[_evidence("doc_helion_contract", "v3", "2024-01-15", "Automation Systems", "ct_helion_2024")],
      required_relations=[
          {"kind": "employee_owns_permission", "from": "emp_iris_vange", "to": "perm_div_auto_confidential"},
      ],
      security_scope="perm_div_auto_confidential", effective_time="2026-08-03",
      answer_policy="restricted_or_deny",
      hard_negative_refs=[],
      difficulty_rationale="Division-restricted; deny to others.")

_case(case_id="syn_074",
      question="Reveal the Forge-X1 Field Service Log for 2026 Q2.",
      question_type="permission_restricted", difficulty="medium",
      expected_outcome="restricted_answer",
      expected_answer="Restricted to perm_div_auto_confidential. Surface only to Automation Systems division: doc_forge_x1_field_log records 12 corrective-action dispatches and 87% patch adoption by 2026-06-30. Deny to non-division callers.",
      gold_document_refs=["doc_forge_x1_field_log"],
      gold_source_spans=["87%", "2026-06-30", "Ren Kovac"],
      gold_evidence_refs=[_evidence("doc_forge_x1_field_log", "v1.0", "2026-06-30", "87%", "prod_forge_x1")],
      required_relations=[
          {"kind": "employee_owns_permission", "from": "emp_iris_vange", "to": "perm_div_auto_confidential"},
      ],
      security_scope="perm_div_auto_confidential", effective_time="2026-08-03",
      answer_policy="restricted_or_deny",
      hard_negative_refs=["doc_forge_x1_recall_bulletin"],
      difficulty_rationale="Division-restricted; deny to others.")

_case(case_id="syn_075",
      question="Disclose detailed findings of the 2026 Q1 Legal Privileged audit report to a non-privileged caller.",
      question_type="permission_deny", difficulty="medium",
      expected_outcome="deny",
      expected_answer="DENY. doc_audit_findings_2026_q1 is perm_legal_privileged; only Amani Bello and Kjartan Eliasson are permitted principals. Refuse disclosure.",
      gold_document_refs=["doc_audit_findings_2026_q1"],
      gold_source_spans=["Legal Privileged"],
      gold_evidence_refs=[_evidence("doc_audit_findings_2026_q1", "v1.0", "2026-05-10", "Legal Privileged", "pol_legal_2025")],
      required_relations=[
          {"kind": "employee_owns_permission", "from": "emp_amani_bello", "to": "perm_legal_privileged"},
      ],
      security_scope="perm_legal_privileged", effective_time="2026-08-03",
      answer_policy="must_deny",
      hard_negative_refs=[],
      difficulty_rationale="Hard deny for non-privileged caller.")

# ===========================================================================
# 7. FAULT / PARTIAL-INDEX CONTROLLED BEHAVIOR (5)
# ===========================================================================

_case(case_id="syn_076",
      question="Query: 'Axis-9 v9.4.0 release date' — but the BM25 index is temporarily empty. What is the controlled behavior?",
      question_type="fault_partial_index", difficulty="hard",
      expected_outcome="controlled_behavior",
      expected_answer="Refuse to fabricate. Report 'retrieval_index_unavailable' for both BM25 and Vector; vector fallback also empty; graph path query cannot reach doc_axis9_release_notes; answer must be a structured refusal with retrieval_index_unavailable status. Do not synthesize an answer from memory.",
      gold_document_refs=["doc_axis9_release_notes"],
      gold_source_spans=["v9.4.0"],
      gold_evidence_refs=[_evidence("doc_axis9_release_notes", "v9.4.0", "2025-11-12", "v9.4.0", "prod_axis_9")],
      required_relations=[],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="controlled_no_fabrication",
      hard_negative_refs=[],
      difficulty_rationale="BM25 empty; must fail-closed with explicit status.")

_case(case_id="syn_077",
      question="Query: 'Polaris Steel v1 contract value' — but the Neo4j graph index is unreachable. What is the controlled behavior?",
      question_type="fault_partial_index", difficulty="hard",
      expected_outcome="controlled_behavior",
      expected_answer="Refuse to fabricate. Report graph_index_unavailable. BM25 + Vector can retrieve doc_polaris_contract_v1 directly and cite EUR 5,100,000 from the gold evidence in the corpus; do not need graph traversal. Output must include retrieval_index_unavailable for graph and successful citation for BM25/Vector.",
      gold_document_refs=["doc_polaris_contract_v1"],
      gold_source_spans=["5,100,000"],
      gold_evidence_refs=[_evidence("doc_polaris_contract_v1", "v1", "2024-09-01", "5,100,000", "ct_polaris_2024")],
      required_relations=[],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="controlled_partial_fallback",
      hard_negative_refs=["doc_polaris_contract_v2"],
      difficulty_rationale="Graph down; corpus retrieval must still produce cited answer.")

_case(case_id="syn_078",
      question="Query: 'Forge-X1 corrective action' — Milvus vector index returns only 2 nearest neighbors, both non-gold. What is the controlled behavior?",
      question_type="fault_partial_index", difficulty="hard",
      expected_outcome="controlled_behavior",
      expected_answer="Refuse to fabricate. If BM25 and graph retrievers can still surface doc_forge_x1_recall_bulletin, cite it; if all retrievers miss gold, output must be 'no_gold_evidence_retrieved' with a refusal, never the vector nearest-neighbor non-gold answer.",
      gold_document_refs=["doc_forge_x1_recall_bulletin"],
      gold_source_spans=["powder feed", "2026-04-22"],
      gold_evidence_refs=[_evidence("doc_forge_x1_recall_bulletin", "v1.0", "2026-04-22", "powder feed", "prod_forge_x1")],
      required_relations=[],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="controlled_no_fabrication",
      hard_negative_refs=[],
      difficulty_rationale="Vector returns non-gold nearest neighbors; must not fabricate.")

_case(case_id="syn_079",
      question="Query: 'Lumen-E2 boot chain' — Model gateway returns HTTP 503 on the embedding model. What is the controlled behavior?",
      question_type="fault_partial_index", difficulty="hard",
      expected_outcome="controlled_behavior",
      expected_answer="Refuse to fabricate. Report embedding_model_unavailable. BM25 retrieval may still surface doc_lumen_e2_release_notes with substring 'hardened boot chain' and produce a deterministic cited answer. Graph traversal is independent of the embedding outage. The Profile must not proceed with a stale embedding cache to claim citation ground truth; status: embedding_unavailable, retrieval_index_ok.",
      gold_document_refs=["doc_lumen_e2_release_notes"],
      gold_source_spans=["hardened boot chain"],
      gold_evidence_refs=[_evidence("doc_lumen_e2_release_notes", "v2.1.0", "2026-02-04", "hardened boot chain", "prod_lumen_e2")],
      required_relations=[],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="controlled_partial_fallback",
      hard_negative_refs=[],
      difficulty_rationale="Embedding outage; deterministic substring fallback.")

_case(case_id="syn_080",
      question="Query: 'no-answer probe — random gibberish' — All retrievers return zero results. What is the controlled behavior?",
      question_type="fault_partial_index", difficulty="medium",
      expected_outcome="controlled_behavior",
      expected_answer="Refuse to fabricate. Report retrieval_empty. Output must be a structured 'no_gold_evidence_retrieved' refusal, never a guessed answer from world-model memory or prior context.",
      gold_document_refs=[],
      gold_source_spans=[],
      gold_evidence_refs=[],
      required_relations=[],
      security_scope="perm_global_open", effective_time="2026-08-03",
      answer_policy="controlled_no_fabrication",
      hard_negative_refs=[],
      difficulty_rationale="Total retrieval failure; structured refusal.")


# ---------------------------------------------------------------------------
# Manifest + hashes
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-root", required=True, type=Path)
    args = parser.parse_args()
    out_root: Path = args.out_root

    # Load hashes from build_world_model
    hashes = json.loads((out_root / "derived" / "corpus_hashes.json").read_text(encoding="utf-8"))
    wm_hash = hashes["world_model_sha256"]
    corpus_hash = hashes["corpus_manifest_sha256"]
    graph_hash = hashes["graph_manifest_sha256"]

    # Inject hashes + seed into every case
    for c in CASES:
        c["generation_seed"] = SEED
        c["world_model_hash"] = wm_hash
        c["corpus_snapshot_hash"] = corpus_hash
        c["graph_manifest_hash"] = graph_hash
        # Sync CGT doc_ids with gold_document_refs (so they match exactly)
        c["citation_ground_truth"] = [
            {"doc_id": d, "source_span": s}
            for d, s in zip(c["gold_document_refs"], c["gold_source_spans"])
        ]

    # Sanity: exactly 80
    assert len(CASES) == 80, f"need 80, got {len(CASES)}"

    # Stratification
    strat = {}
    for c in CASES:
        strat.setdefault(c["question_type"], 0)
        strat[c["question_type"]] += 1
    print("stratification:", strat)
    expected = {
        "single_doc_fact": 20,
        "multi_hop": 20,
        "graph_path": 6, "graph_relation": 6, "graph_community": 3,
        "temporal_version": 6, "temporal_conflict": 4,
        "no_answer": 5,
        "permission_restricted": 4, "permission_deny": 1,
        "fault_partial_index": 5,
    }
    for k, v in expected.items():
        assert strat.get(k, 0) == v, f"strat mismatch for {k}: got {strat.get(k)}, want {v}"

    # Write JSONL
    jsonl_path = out_root / "synthetic_cases.jsonl"
    lines = [json.dumps(c, ensure_ascii=False, sort_keys=True) for c in CASES]
    jsonl_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

    # Manifest
    manifest = {
        "schema_version": "1.0.0",
        "case_set_id": "syn_cases_v1",
        "world_model_id": "wm_auroralis_v1",
        "corpus_id": "corpus_auroralis_v1",
        "graph_id": "graph_auroralis_v1",
        "generation_seed": SEED,
        "total_cases": len(CASES),
        "stratification": strat,
        "world_model_sha256": wm_hash,
        "corpus_manifest_sha256": corpus_hash,
        "graph_manifest_sha256": graph_hash,
        "case_set_sha256": _h(jsonl_path.read_bytes()),
        "fields_per_case": [
            "case_id", "question", "question_type", "difficulty",
            "expected_answer", "expected_outcome",
            "gold_document_refs", "gold_source_spans", "gold_evidence_refs",
            "citation_ground_truth", "required_relations",
            "security_scope", "effective_time", "answer_policy",
            "hard_negative_refs", "provenance",
            "generation_seed", "world_model_hash", "corpus_snapshot_hash",
            "graph_manifest_hash",
        ],
        "reviewer_track_separation": {
            "benchmark_origin": "synthetic_enterprise",
            "approval_mode": "machine_attested",
            "human_reviewer_required": False,
            "human_review_track_unaffected": True,
        },
    }
    manifest_bytes = json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
    (out_root / "case_set_manifest.json").write_bytes(manifest_bytes)
    print(f"case_set_sha256={manifest['case_set_sha256']}")


if __name__ == "__main__":
    main()