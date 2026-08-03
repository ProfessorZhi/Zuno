"""Build the synthetic enterprise world model deterministically.

This script is the single source of truth for the world model used by the
PHASE22 synthetic benchmark track. It writes:

  - world_model.json
  - corpus/*.md (>=48 documents)
  - corpus_manifest.json
  - graph_manifest.json
  - source_span_index.json
  - corpus_hashes.json

The script is idempotent: re-running with the same SEED produces identical
files and identical SHA-256 hashes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SEED = "phase22-synthetic-2026-08-03-auroralis-v1"
GENERATION_TIME_UTC = "2026-08-03T01:37:00Z"


def _h(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


# ---------------------------------------------------------------------------
# Entities (fictional)
# ---------------------------------------------------------------------------

COMPANY = {
    "legal_name": "Auroralis Manufacturing Group N.V.",
    "short_name": "Auroralis",
    "headquarters": "Reykjavik Operations Center, Iceland (fictional)",
    "founded_year": 1998,
    "fiscal_year_end": "12-31",
    "primary_industries": ["industrial_automation", "edge_software", "additive_manufacturing"],
    "operating_regions": ["EMEA", "AMER", "APAC"],
    "public_ticker": "AUR-X",
    "internal_codename": "Project Northwind",
}

DIVISIONS = [
    {"division_id": "div_auto", "name": "Auroralis Automation Systems", "region": "EMEA", "lead_employee_id": "emp_iris_vange"},
    {"division_id": "div_edge", "name": "Auroralis Edge Compute", "region": "AMER", "lead_employee_id": "emp_marcus_tien"},
    {"division_id": "div_addmfg", "name": "Auroralis Additive Manufacturing", "region": "APAC", "lead_employee_id": "emp_yui_nakajima"},
    {"division_id": "div_corp", "name": "Auroralis Corporate Services", "region": "EMEA", "lead_employee_id": "emp_solveig_hagen"},
]

EMPLOYEES = [
    {"employee_id": "emp_iris_vange", "full_name": "Iris Vange", "title": "President, Automation Systems", "division_id": "div_auto", "reports_to": "ceo_kjartan_eli", "tenure_start": "2017-04-03"},
    {"employee_id": "emp_marcus_tien", "full_name": "Marcus Tien", "title": "President, Edge Compute", "division_id": "div_edge", "reports_to": "ceo_kjartan_eli", "tenure_start": "2019-09-12"},
    {"employee_id": "emp_yui_nakajima", "full_name": "Yui Nakajima", "title": "President, Additive Manufacturing", "division_id": "div_addmfg", "reports_to": "ceo_kjartan_eli", "tenure_start": "2020-02-18"},
    {"employee_id": "emp_solveig_hagen", "full_name": "Solveig Hagen", "title": "Chief Corporate Officer", "division_id": "div_corp", "reports_to": "ceo_kjartan_eli", "tenure_start": "2014-06-01"},
    {"employee_id": "emp_dmitri_orel", "full_name": "Dmitri Orel", "title": "Chief Financial Officer", "division_id": "div_corp", "reports_to": "ceo_kjartan_eli", "tenure_start": "2022-01-10"},
    {"employee_id": "emp_priya_kaur", "full_name": "Priya Kaur", "title": "Chief Information Security Officer", "division_id": "div_corp", "reports_to": "ceo_kjartan_eli", "tenure_start": "2021-11-22"},
    {"employee_id": "emp_lukas_wenger", "full_name": "Lukas Wenger", "title": "Head of Procurement", "division_id": "div_corp", "reports_to": "emp_solveig_hagen", "tenure_start": "2018-08-14"},
    {"employee_id": "emp_amani_bello", "full_name": "Amani Bello", "title": "General Counsel", "division_id": "div_corp", "reports_to": "ceo_kjartan_eli", "tenure_start": "2016-03-07"},
    {"employee_id": "emp_haruto_soma", "full_name": "Haruto Soma", "title": "Director, Robotics R&D", "division_id": "div_auto", "reports_to": "emp_iris_vange", "tenure_start": "2018-05-09"},
    {"employee_id": "emp_eli_persson", "full_name": "Eli Persson", "title": "Director, Embedded Firmware", "division_id": "div_edge", "reports_to": "emp_marcus_tien", "tenure_start": "2020-07-21"},
    {"employee_id": "emp_nadya_soroka", "full_name": "Nadya Soroka", "title": "Director, Quality & Compliance", "division_id": "div_corp", "reports_to": "emp_solveig_hagen", "tenure_start": "2019-02-04"},
    {"employee_id": "emp_ren_kovac", "full_name": "Ren Kovac", "title": "Director, Field Service Operations", "division_id": "div_auto", "reports_to": "emp_iris_vange", "tenure_start": "2017-09-19"},
]

CEO = {"employee_id": "ceo_kjartan_eli", "full_name": "Kjartan Eliasson", "title": "Group Chief Executive Officer", "tenure_start": "2015-01-05"}

PRODUCTS = [
    {"product_id": "prod_axis_9", "name": "Axis-9 Industrial Controller", "division_id": "div_auto", "release_version": "v9.4.0", "release_date": "2025-11-12", "current_status": "active"},
    {"product_id": "prod_axis_8", "name": "Axis-8 Industrial Controller", "division_id": "div_auto", "release_version": "v8.7.2", "release_date": "2023-06-30", "current_status": "maintenance_only"},
    {"product_id": "prod_lumen_e2", "name": "Lumen-E2 Edge Compute Appliance", "division_id": "div_edge", "release_version": "v2.1.0", "release_date": "2026-02-04", "current_status": "active"},
    {"product_id": "prod_lumen_e1", "name": "Lumen-E1 Edge Compute Appliance", "division_id": "div_edge", "release_version": "v1.8.5", "release_date": "2024-05-22", "current_status": "maintenance_only"},
    {"product_id": "prod_forge_x1", "name": "Forge-X1 Additive Manufacturing Cell", "division_id": "div_addmfg", "release_version": "v1.3.1", "release_date": "2025-08-19", "current_status": "active"},
    {"product_id": "prod_northwind_sdk", "name": "Northwind Industrial SDK", "division_id": "div_auto", "release_version": "v3.0.0", "release_date": "2026-01-15", "current_status": "active"},
]

SUPPLIERS = [
    {"supplier_id": "sup_helion_motors", "name": "Helion Motors GmbH (fictional)", "country": "Germany", "category": "servo_motors", "preferred_status": "approved"},
    {"supplier_id": "sup_kobal_silicon", "name": "Kobal Silicon S.A. (fictional)", "country": "France", "category": "industrial_sensors", "preferred_status": "approved"},
    {"supplier_id": "sup_meridian_logistics", "name": "Meridian Logistics Co. (fictional)", "country": "Singapore", "category": "freight_forwarding", "preferred_status": "approved"},
    {"supplier_id": "sup_polaris_steel", "name": "Polaris Steel Industries (fictional)", "country": "Sweden", "category": "raw_materials", "preferred_status": "conditional"},
    {"supplier_id": "sup_ozone_chem", "name": "Ozone Chemicals Ltd. (fictional)", "country": "India", "category": "specialty_chemicals", "preferred_status": "probation"},
]

CONTRACTS = [
    {"contract_id": "ct_helion_2024", "supplier_id": "sup_helion_motors", "division_id": "div_auto", "effective_at": "2024-01-15", "expires_at": "2027-01-14", "value_eur": 12500000, "owner_employee_id": "emp_lukas_wenger", "contract_type": "supply_master_agreement", "version": "v3"},
    {"contract_id": "ct_kobal_2025", "supplier_id": "sup_kobal_silicon", "division_id": "div_edge", "effective_at": "2025-03-01", "expires_at": "2028-02-29", "value_eur": 7400000, "owner_employee_id": "emp_lukas_wenger", "contract_type": "supply_master_agreement", "version": "v2"},
    {"contract_id": "ct_meridian_2025", "supplier_id": "sup_meridian_logistics", "division_id": "div_corp", "effective_at": "2025-06-01", "expires_at": "2026-12-31", "value_eur": 3200000, "owner_employee_id": "emp_lukas_wenger", "contract_type": "logistics_msa", "version": "v1", "supersedes": None},
    {"contract_id": "ct_polaris_2024", "supplier_id": "sup_polaris_steel", "division_id": "div_addmfg", "effective_at": "2024-09-01", "expires_at": "2025-08-31", "value_eur": 5100000, "owner_employee_id": "emp_lukas_wenger", "contract_type": "supply_master_agreement", "version": "v1", "superseded_by": "ct_polaris_2025"},
    {"contract_id": "ct_polaris_2025", "supplier_id": "sup_polaris_steel", "division_id": "div_addmfg", "effective_at": "2025-09-01", "expires_at": "2027-08-31", "value_eur": 5750000, "owner_employee_id": "emp_lukas_wenger", "contract_type": "supply_master_agreement", "version": "v2", "supersedes": "ct_polaris_2024"},
]

POLICIES = [
    {"policy_id": "pol_sec_2026", "title": "Information Security Policy (2026 Edition)", "owner_employee_id": "emp_priya_kaur", "effective_at": "2026-01-01", "version": "v4.2", "scope": "global", "supersedes": "pol_sec_2024"},
    {"policy_id": "pol_sec_2024", "title": "Information Security Policy (2024 Edition)", "owner_employee_id": "emp_priya_kaur", "effective_at": "2024-01-01", "version": "v4.1", "scope": "global", "superseded_by": "pol_sec_2026"},
    {"policy_id": "pol_procure_2025", "title": "Procurement and Supplier Onboarding Policy", "owner_employee_id": "emp_lukas_wenger", "effective_at": "2025-04-01", "version": "v2.0", "scope": "global"},
    {"policy_id": "pol_quality_2025", "title": "Quality Management System Policy", "owner_employee_id": "emp_nadya_soroka", "effective_at": "2025-07-15", "version": "v3.1", "scope": "global"},
    {"policy_id": "pol_legal_2025", "title": "Export Control and Trade Compliance Policy", "owner_employee_id": "emp_amani_bello", "effective_at": "2025-02-01", "version": "v1.5", "scope": "global"},
]

PROJECTS = [
    {"project_id": "proj_northwind", "name": "Project Northwind - Industrial SDK Modernization", "division_id": "div_auto", "sponsor_employee_id": "ceo_kjartan_eli", "start_date": "2025-09-01", "target_close": "2026-12-31", "budget_eur": 22000000, "status": "on_track"},
    {"project_id": "proj_lumenx", "name": "Project Lumen-X - Edge Inference Expansion", "division_id": "div_edge", "sponsor_employee_id": "emp_marcus_tien", "start_date": "2026-01-15", "target_close": "2027-06-30", "budget_eur": 14500000, "status": "at_risk"},
    {"project_id": "proj_forge2", "name": "Project Forge-II - Second Generation Additive Cell", "division_id": "div_addmfg", "sponsor_employee_id": "emp_yui_nakajima", "start_date": "2025-11-01", "target_close": "2027-02-28", "budget_eur": 9800000, "status": "on_track"},
]

EVENTS = [
    {"event_id": "evt_axis_9_release", "product_id": "prod_axis_9", "kind": "release", "occurred_at": "2025-11-12", "actor_employee_id": "emp_haruto_soma", "summary": "Axis-9 v9.4.0 released to manufacturing customers."},
    {"event_id": "evt_axis_8_eol", "product_id": "prod_axis_8", "kind": "end_of_life_announcement", "occurred_at": "2026-03-01", "actor_employee_id": "emp_iris_vange", "summary": "Axis-8 enters maintenance-only mode; EOL planned for 2027-06-30."},
    {"event_id": "evt_lumen_e2_release", "product_id": "prod_lumen_e2", "kind": "release", "occurred_at": "2026-02-04", "actor_employee_id": "emp_eli_persson", "summary": "Lumen-E2 v2.1.0 released with hardened boot chain."},
    {"event_id": "evt_forge_x1_recall", "product_id": "prod_forge_x1", "kind": "field_action", "occurred_at": "2026-04-22", "actor_employee_id": "emp_nadya_soroka", "summary": "Voluntary firmware corrective action issued for Forge-X1 powder feed subsystem."},
    {"event_id": "evt_polaris_renewal", "supplier_id": "sup_polaris_steel", "kind": "contract_renewal", "occurred_at": "2025-09-01", "actor_employee_id": "emp_lukas_wenger", "summary": "Polaris Steel contract renewed at EUR 5.75M effective 2025-09-01."},
    {"event_id": "evt_policy_2026", "policy_id": "pol_sec_2026", "kind": "policy_publication", "occurred_at": "2026-01-01", "actor_employee_id": "emp_priya_kaur", "summary": "2026 Information Security Policy published, superseding 2024 edition."},
]

PERMISSIONS = [
    {"permission_id": "perm_div_auto_confidential", "scope_label": "division:automation/confidential", "owner_employee_id": "emp_iris_vange", "visibility": "division_restricted"},
    {"permission_id": "perm_legal_privileged", "scope_label": "legal/privileged", "owner_employee_id": "emp_amani_bello", "visibility": "role_restricted", "members": ["emp_amani_bello", "ceo_kjartan_eli"]},
    {"permission_id": "perm_finance_audit", "scope_label": "finance/audit", "owner_employee_id": "emp_dmitri_orel", "visibility": "role_restricted", "members": ["emp_dmitri_orel", "emp_priya_kaur"]},
    {"permission_id": "perm_global_open", "scope_label": "global/open", "owner_employee_id": "emp_solveig_hagen", "visibility": "global"},
]

SECURITY_SCOPES = {
    "perm_div_auto_confidential": ["div_auto"],
    "perm_legal_privileged": ["legal"],
    "perm_finance_audit": ["finance"],
    "perm_global_open": ["*"],
}

# ---------------------------------------------------------------------------
# Relations (graph)
# ---------------------------------------------------------------------------

RELATIONS = []


def _add(kind, from_id, from_type, to_id, to_type):
    rid = f"rel_{kind}_{from_id}_{to_id}"
    RELATIONS.append({
        "relation_id": rid,
        "kind": kind,
        "from_id": from_id,
        "from_type": from_type,
        "to_id": to_id,
        "to_type": to_type,
    })


for emp in EMPLOYEES:
    _add("employee_in_division", emp["employee_id"], "employee", emp["division_id"], "division")
    _add("reports_to", emp["employee_id"], "employee", emp["reports_to"], "employee")

for prod in PRODUCTS:
    _add("product_in_division", prod["product_id"], "product", prod["division_id"], "division")

for sup in SUPPLIERS:
    _add("supplier_serves_company", sup["supplier_id"], "supplier", "company_auroralis", "company")

for ct in CONTRACTS:
    _add("contract_with_supplier", ct["contract_id"], "contract", ct["supplier_id"], "supplier")
    _add("contract_owned_by", ct["contract_id"], "contract", ct["owner_employee_id"], "employee")
    _add("contract_serves_division", ct["contract_id"], "contract", ct["division_id"], "division")

for pol in POLICIES:
    _add("policy_owned_by", pol["policy_id"], "policy", pol["owner_employee_id"], "employee")

for prj in PROJECTS:
    _add("project_owned_by_division", prj["project_id"], "project", prj["division_id"], "division")
    _add("project_sponsored_by", prj["project_id"], "project", prj["sponsor_employee_id"], "employee")

for ev in EVENTS:
    if "product_id" in ev:
        _add("event_about_product", ev["event_id"], "event", ev["product_id"], "product")
    if "supplier_id" in ev:
        _add("event_about_supplier", ev["event_id"], "event", ev["supplier_id"], "supplier")
    if "policy_id" in ev:
        _add("event_about_policy", ev["event_id"], "event", ev["policy_id"], "policy")
    _add("event_actor", ev["event_id"], "event", ev["actor_employee_id"], "employee")

# Cross-links for multi-hop retrieval
_add("project_delivers_product", "proj_northwind", "project", "prod_northwind_sdk", "product")
_add("project_delivers_product", "proj_lumenx", "project", "prod_lumen_e2", "product")
_add("project_delivers_product", "proj_forge2", "project", "prod_forge_x1", "product")
_add("division_lead_employee", "div_auto", "division", "emp_iris_vange", "employee")
_add("division_lead_employee", "div_edge", "division", "emp_marcus_tien", "employee")
_add("division_lead_employee", "div_addmfg", "division", "emp_yui_nakajima", "employee")
_add("division_lead_employee", "div_corp", "division", "emp_solveig_hagen", "employee")
_add("employee_owns_permission", "emp_iris_vange", "employee", "perm_div_auto_confidential", "permission")
_add("employee_owns_permission", "emp_amani_bello", "employee", "perm_legal_privileged", "permission")
_add("employee_owns_permission", "emp_dmitri_orel", "employee", "perm_finance_audit", "permission")
_add("employee_owns_permission", "emp_solveig_hagen", "employee", "perm_global_open", "permission")
_add("product_owner", "prod_axis_9", "product", "emp_haruto_soma", "employee")
_add("product_owner", "prod_axis_8", "product", "emp_iris_vange", "employee")
_add("product_owner", "prod_lumen_e2", "product", "emp_eli_persson", "employee")
_add("product_owner", "prod_lumen_e1", "product", "emp_marcus_tien", "employee")
_add("product_owner", "prod_forge_x1", "product", "emp_yui_nakajima", "employee")
_add("product_owner", "prod_northwind_sdk", "product", "emp_haruto_soma", "employee")
_add("contract_supersedes", "ct_polaris_2025", "contract", "ct_polaris_2024", "contract")
_add("policy_supersedes", "pol_sec_2026", "policy", "pol_sec_2024", "policy")


# ---------------------------------------------------------------------------
# Documents (>= 48)
# ---------------------------------------------------------------------------

DOCS = []


def _doc(doc_id, title, division_id, owner_employee_id, version, effective_at, security_scope, kind, source_topic_refs, body):
    DOCS.append({
        "document_id": doc_id,
        "title": title,
        "division_id": division_id,
        "owner_employee_id": owner_employee_id,
        "version": version,
        "effective_at": effective_at,
        "security_scope": security_scope,
        "kind": kind,
        "source_topic_refs": source_topic_refs,
        "body": body,
    })


# === Org and biographies ===
_doc("doc_org_chart_2026",
     "Auroralis Organizational Chart - 2026 Q2",
     "div_corp", "emp_solveig_hagen", "v2026.Q2", "2026-04-01",
     "perm_global_open", "org_chart", ["employees", "divisions"],
     "Auroralis is led by CEO Kjartan Eliasson (tenure start 2015-01-05). Four divisions report directly to the CEO: Automation Systems (President Iris Vange, EMEA), Edge Compute (President Marcus Tien, AMER), Additive Manufacturing (President Yui Nakajima, APAC), and Corporate Services (Chief Corporate Officer Solveig Hagen, EMEA). Direct corporate reports include CFO Dmitri Orel, CISO Priya Kaur, and General Counsel Amani Bello. Procurement head Lukas Wenger reports to Solveig Hagen; Quality director Nadya Soroka reports to Solveig Hagen; Robotics R&D director Haruto Soma reports to Iris Vange; Embedded Firmware director Eli Persson reports to Marcus Tien; Field Service director Ren Kovac reports to Iris Vange.")

for emp in EMPLOYEES:
    body = f"{emp['full_name']} serves as {emp['title']} in the {emp['division_id']} division, tenure start {emp['tenure_start']}. Reports to {emp['reports_to']}."
    _doc(f"doc_bio_{emp['employee_id']}",
         f"{emp['full_name']} - Biography",
         "div_corp", "emp_solveig_hagen", "v1.0", "2025-12-15",
         "perm_global_open", "biography", [emp["employee_id"]],
         body)
    # Short alias (used by case references): emp_iris_vange -> doc_iris_bio
    parts = emp['employee_id'].split('_')
    short_id = "doc_" + parts[1] + "_bio"
    _doc(short_id,
         f"{emp['full_name']} - Biography (Alias)",
         "div_corp", "emp_solveig_hagen", "v1.0", "2025-12-15",
         "perm_global_open", "biography", [emp["employee_id"]],
         body)

_doc("doc_ceo_bio", "Kjartan Eliasson - CEO Biography",
     "div_corp", "emp_solveig_hagen", "v1.0", "2025-12-15",
     "perm_global_open", "biography", ["ceo_kjartan_eli"],
     "Kjartan Eliasson is Group Chief Executive Officer, tenure start 2015-01-05. All four division presidents report directly to the CEO. CFO, CISO, and General Counsel are direct reports.")

# === Products and release notes ===
_doc("doc_axis9_release_notes",
     "Axis-9 Controller v9.4.0 - Release Notes",
     "div_auto", "emp_haruto_soma", "v9.4.0", "2025-11-12",
     "perm_global_open", "release_notes", ["prod_axis_9", "evt_axis_9_release"],
     "Axis-9 Industrial Controller v9.4.0 was released on 2025-11-12 by Haruto Soma (Director, Robotics R&D). The release introduces deterministic motion-control scheduling and a hardened CIP safety stack. The Axis-9 is in active status in the Automation Systems division. v9.4.0 supersedes v9.3.x for general availability.")

_doc("doc_axis8_eol_memo",
     "Axis-8 End-of-Life Transition Memo",
     "div_auto", "emp_iris_vange", "v1.0", "2026-03-01",
     "perm_global_open", "memo", ["prod_axis_8", "evt_axis_8_eol"],
     "On 2026-03-01, Iris Vange (President, Automation Systems) announced that Axis-8 Industrial Controller has entered maintenance-only mode. End-of-life is planned for 2027-06-30. Customers are advised to migrate to Axis-9 v9.4.x.")

_doc("doc_lumen_e2_release_notes",
     "Lumen-E2 Appliance v2.1.0 - Release Notes",
     "div_edge", "emp_eli_persson", "v2.1.0", "2026-02-04",
     "perm_global_open", "release_notes", ["prod_lumen_e2", "evt_lumen_e2_release"],
     "Lumen-E2 Edge Compute Appliance v2.1.0 was released on 2026-02-04 by Eli Persson (Director, Embedded Firmware). The release includes a hardened boot chain and signed firmware envelope.")

_doc("doc_lumen_e1_eol_memo",
     "Lumen-E1 End-of-Sale Memo",
     "div_edge", "emp_marcus_tien", "v1.0", "2024-05-22",
     "perm_global_open", "memo", ["prod_lumen_e1"],
     "Effective 2024-05-22, the Lumen-E1 Edge Compute Appliance is end-of-sale and enters maintenance-only support. Marcus Tien (President, Edge Compute) signed the memo. Customers should evaluate Lumen-E2 v2.1.x as the successor.")

_doc("doc_forge_x1_release_notes",
     "Forge-X1 Cell v1.3.1 - Release Notes",
     "div_addmfg", "emp_yui_nakajima", "v1.3.1", "2025-08-19",
     "perm_global_open", "release_notes", ["prod_forge_x1"],
     "Forge-X1 Additive Manufacturing Cell v1.3.1 was released on 2025-08-19 by Yui Nakajima (President, Additive Manufacturing). The release introduces a closed-loop powder feed sensor.")

_doc("doc_forge_x1_recall_bulletin",
     "Forge-X1 Powder Feed Corrective Action Bulletin",
     "div_addmfg", "emp_nadya_soroka", "v1.0", "2026-04-22",
     "perm_global_open", "field_bulletin", ["prod_forge_x1", "evt_forge_x1_recall"],
     "On 2026-04-22, Nadya Soroka (Director, Quality & Compliance) issued a voluntary firmware corrective action for Forge-X1 v1.3.x powder feed subsystem. Customers must apply the patch within 30 days.")

_doc("doc_northwind_sdk_overview",
     "Northwind Industrial SDK v3.0 - Architecture Overview",
     "div_auto", "emp_haruto_soma", "v3.0.0", "2026-01-15",
     "perm_global_open", "architecture", ["prod_northwind_sdk", "proj_northwind"],
     "The Northwind Industrial SDK v3.0.0 was released on 2026-01-15 by Haruto Soma. Northwind is the canonical SDK for the Axis-9 controller family and is the primary deliverable of Project Northwind (sponsor: CEO Kjartan Eliasson).")

# === Contracts and supplier briefs ===
_doc("doc_helion_contract",
     "Helion Motors Master Supply Agreement (2024 Edition)",
     "div_auto", "emp_lukas_wenger", "v3", "2024-01-15",
     "perm_div_auto_confidential", "contract_summary", ["sup_helion_motors", "ct_helion_2024"],
     "Helion Motors master supply agreement v3, effective 2024-01-15 through 2027-01-14, total value EUR 12,500,000. Owner: Lukas Wenger (Head of Procurement). Serves the Automation Systems division (Iris Vange).")

_doc("doc_kobal_contract",
     "Kobal Silicon Master Supply Agreement (2025 Edition)",
     "div_edge", "emp_lukas_wenger", "v2", "2025-03-01",
     "perm_div_auto_confidential", "contract_summary", ["sup_kobal_silicon", "ct_kobal_2025"],
     "Kobal Silicon master supply agreement v2, effective 2025-03-01 through 2028-02-29, total value EUR 7,400,000. Owner: Lukas Wenger. Serves the Edge Compute division (Marcus Tien).")

_doc("doc_meridian_contract",
     "Meridian Logistics MSA - Service Description",
     "div_corp", "emp_lukas_wenger", "v1", "2025-06-01",
     "perm_global_open", "contract_summary", ["sup_meridian_logistics", "ct_meridian_2025"],
     "Meridian Logistics master service agreement v1, effective 2025-06-01 through 2026-12-31, total value EUR 3,200,000. Owner: Lukas Wenger. Serves Corporate Services.")

_doc("doc_polaris_contract_v1",
     "Polaris Steel MSA (2024 Edition) - Archived Summary",
     "div_addmfg", "emp_lukas_wenger", "v1", "2024-09-01",
     "perm_global_open", "contract_summary", ["sup_polaris_steel", "ct_polaris_2024"],
     "Polaris Steel master supply agreement v1, effective 2024-09-01 through 2025-08-31, total value EUR 5,100,000. Owner: Lukas Wenger. Superseded by v2 (ct_polaris_2025) on 2025-09-01.")

_doc("doc_polaris_contract_v2",
     "Polaris Steel MSA (2025 Edition) - Summary",
     "div_addmfg", "emp_lukas_wenger", "v2", "2025-09-01",
     "perm_global_open", "contract_summary", ["sup_polaris_steel", "ct_polaris_2025"],
     "Polaris Steel master supply agreement v2, effective 2025-09-01 through 2027-08-31, total value EUR 5,750,000. Owner: Lukas Wenger. Serves Additive Manufacturing (Yui Nakajima). Supersedes the 2024 v1 edition.")

for sup in SUPPLIERS:
    _doc(f"doc_supplier_brief_{sup['supplier_id']}",
         f"{sup['name'].split(' (')[0]} - Supplier Brief",
         "div_corp", "emp_lukas_wenger", "v1.0", "2025-12-01",
         "perm_global_open", "supplier_brief", [sup["supplier_id"]],
         f"{sup['name']} ({sup['country']}) is a {sup['category']} supplier in {sup['preferred_status']} status. Owner: Lukas Wenger.")

# === Policies ===
_doc("doc_security_policy_2024",
     "Information Security Policy (2024 Edition)",
     "div_corp", "emp_priya_kaur", "v4.1", "2024-01-01",
     "perm_global_open", "policy", ["pol_sec_2024"],
     "Information Security Policy v4.1, effective 2024-01-01, owner Priya Kaur (CISO). Superseded on 2026-01-01 by the 2026 edition.")

_doc("doc_security_policy_2026",
     "Information Security Policy (2026 Edition)",
     "div_corp", "emp_priya_kaur", "v4.2", "2026-01-01",
     "perm_global_open", "policy", ["pol_sec_2026"],
     "Information Security Policy v4.2, effective 2026-01-01, owner Priya Kaur. Supersedes the 2024 edition. Adds explicit guidance on retrieval-augmented system citation and provenance.")

_doc("doc_procurement_policy",
     "Procurement and Supplier Onboarding Policy",
     "div_corp", "emp_lukas_wenger", "v2.0", "2025-04-01",
     "perm_global_open", "policy", ["pol_procure_2025"],
     "Procurement and Supplier Onboarding Policy v2.0, effective 2025-04-01, owner Lukas Wenger. Defines approved / conditional / probation supplier tiers.")

_doc("doc_quality_policy",
     "Quality Management System Policy",
     "div_corp", "emp_nadya_soroka", "v3.1", "2025-07-15",
     "perm_global_open", "policy", ["pol_quality_2025"],
     "Quality Management System Policy v3.1, effective 2025-07-15, owner Nadya Soroka. Defines field-action and corrective-action procedures.")

_doc("doc_export_policy",
     "Export Control and Trade Compliance Policy",
     "div_corp", "emp_amani_bello", "v1.5", "2025-02-01",
     "perm_legal_privileged", "policy", ["pol_legal_2025"],
     "Export Control and Trade Compliance Policy v1.5, effective 2025-02-01, owner Amani Bello (General Counsel). Legal privileged; restricted to members of the legal privilege list (Amani Bello, Kjartan Eliasson).")

# === Projects ===
_doc("doc_northwind_charter",
     "Project Northwind - Charter and Milestones",
     "div_auto", "ceo_kjartan_eli", "v1.2", "2025-09-01",
     "perm_div_auto_confidential", "project_charter", ["proj_northwind"],
     "Project Northwind is the modernization of the Northwind Industrial SDK. Sponsor: CEO Kjartan Eliasson. Division: Automation Systems. Budget EUR 22,000,000. Start 2025-09-01, target close 2026-12-31. Status: on_track. Primary deliverable: Northwind SDK v3.0.0 (released 2026-01-15).")

_doc("doc_lumenx_charter",
     "Project Lumen-X - Charter and Risk Register",
     "div_edge", "emp_marcus_tien", "v1.0", "2026-01-15",
     "perm_div_auto_confidential", "project_charter", ["proj_lumenx"],
     "Project Lumen-X expands edge inference capacity. Sponsor: Marcus Tien. Budget EUR 14,500,000. Start 2026-01-15, target close 2027-06-30. Status: at_risk. Primary deliverable: Lumen-E2 v2.1.x line.")

_doc("doc_forge2_charter",
     "Project Forge-II - Charter and BOM",
     "div_addmfg", "emp_yui_nakajima", "v1.1", "2025-11-01",
     "perm_global_open", "project_charter", ["proj_forge2"],
     "Project Forge-II develops the second-generation Forge cell. Sponsor: Yui Nakajima. Budget EUR 9,800,000. Start 2025-11-01, target close 2027-02-28. Status: on_track.")

_doc("doc_northwind_status_2026_q2",
     "Project Northwind - Status Report 2026 Q2",
     "div_auto", "emp_haruto_soma", "v1.0", "2026-07-05",
     "perm_div_auto_confidential", "status_report", ["proj_northwind", "prod_northwind_sdk"],
     "Northwind Q2 2026 status: SDK v3.0.0 GA shipped 2026-01-15. Axis-9 controller integration completed. Risk: external model gateway latency remains within tolerance.")

_doc("doc_lumenx_status_2026_q2",
     "Project Lumen-X - Status Report 2026 Q2",
     "div_edge", "emp_eli_persson", "v1.0", "2026-07-12",
     "perm_div_auto_confidential", "status_report", ["proj_lumenx", "prod_lumen_e2"],
     "Lumen-X Q2 2026 status: Lumen-E2 v2.1.0 GA shipped 2026-02-04. Risk register highlights supplier qualification gap for Kobal Silicon incident (2026-03-19).")

_doc("doc_forge2_status_2026_q2",
     "Project Forge-II - Status Report 2026 Q2",
     "div_addmfg", "emp_yui_nakajima", "v1.0", "2026-07-10",
     "perm_global_open", "status_report", ["proj_forge2", "prod_forge_x1"],
     "Forge-II Q2 2026 status: BOM freeze in progress. Powder feed corrective action (2026-04-22) closed.")

_doc("doc_northwind_meeting_minutes",
     "Northwind Steering Committee - Minutes 2026-06-15",
     "div_auto", "ceo_kjartan_eli", "v1.0", "2026-06-16",
     "perm_div_auto_confidential", "minutes", ["proj_northwind", "emp_haruto_soma"],
     "Northwind steering committee met 2026-06-15 chaired by Kjartan Eliasson. Haruto Soma reported SDK v3.0.0 GA on 2026-01-15; Axis-9 integration milestones on schedule.")

# === Field logs and incidents ===
_doc("doc_forge_x1_field_log",
     "Forge-X1 Field Service Log Excerpt (2026 Q2)",
     "div_addmfg", "emp_ren_kovac", "v1.0", "2026-06-30",
     "perm_div_auto_confidential", "field_log", ["prod_forge_x1", "evt_forge_x1_recall"],
     "Forge-X1 Q2 2026 field service log: 12 corrective-action dispatches executed by Ren Kovac's team. Patch adoption: 87% by 2026-06-30.")

_doc("doc_iris_field_visit",
     "Iris Vange Field Visit Notes - Hannover 2026-05-04",
     "div_auto", "emp_iris_vange", "v1.0", "2026-05-05",
     "perm_div_auto_confidential", "field_notes", ["sup_helion_motors", "ct_helion_2024"],
     "Iris Vange visited Helion Motors (Hannover) on 2026-05-04 to review the v3 supply agreement (effective 2024-01-15) and Axis-9 servo delivery schedule.")

_doc("doc_quality_audit_2026_q1",
     "Quality System Audit - 2026 Q1",
     "div_corp", "emp_nadya_soroka", "v1.0", "2026-04-30",
     "perm_global_open", "audit_report", ["pol_quality_2025", "sup_polaris_steel"],
     "Q1 2026 quality audit findings: Polaris Steel remains in 'conditional' tier pending powder-metallurgy certification. Forge-X1 corrective action tracking on plan.")

_doc("doc_kobal_quality_incident",
     "Kobal Silicon Quality Incident Report - 2026-03-19",
     "div_edge", "emp_nadya_soroka", "v1.0", "2026-03-22",
     "perm_div_auto_confidential", "incident_report", ["sup_kobal_silicon", "ct_kobal_2025"],
     "On 2026-03-19 Nadya Soroka recorded a non-conformance at Kobal Silicon involving a sensor calibration drift. Root cause traced to environmental chamber calibration. Supplier response accepted; corrective action closed 2026-04-08.")

# === Privileged / restricted ===
_doc("doc_audit_findings_2026_q1",
     "Internal Audit Findings - 2026 Q1 (Legal Privileged)",
     "div_corp", "emp_amani_bello", "v1.0", "2026-05-10",
     "perm_legal_privileged", "audit_report", ["pol_legal_2025"],
     "Privileged and confidential. Prepared by Amani Bello (General Counsel). Restricted to the legal privilege list: Amani Bello, Kjartan Eliasson. Contains attorney work product on export-control screening for the Lumen-E2 line.")

_doc("doc_audit_findings_2025_q4",
     "Internal Audit Findings - 2025 Q4 (Finance Restricted)",
     "div_corp", "emp_dmitri_orel", "v1.0", "2026-02-15",
     "perm_finance_audit", "audit_report", ["ct_polaris_2025"],
     "Finance restricted. Prepared by Dmitri Orel (CFO). Restricted to the finance/audit role group: Dmitri Orel, Priya Kaur. Reviews Polaris Steel v2 contract variance vs forecast.")

# === Calendars and corporate ===
_doc("doc_corp_calendar_2026",
     "Auroralis Corporate Calendar - 2026",
     "div_corp", "emp_solveig_hagen", "v1.0", "2026-01-01",
     "perm_global_open", "calendar", [],
     "Auroralis 2026 corporate calendar (fictional). Lists fiscal-year milestones, board meeting dates, and major product release windows: Axis-9 v9.4.0 (2025-11-12), Lumen-E2 v2.1.0 (2026-02-04), Northwind SDK v3.0.0 (2026-01-15).")

# Sanity check
assert len(DOCS) >= 48, f"Need >=48 docs, have {len(DOCS)}"


# ---------------------------------------------------------------------------
# Render & hash
# ---------------------------------------------------------------------------

def render_doc_markdown(doc: dict) -> str:
    refs = "\n".join(f"- {ref}" for ref in doc["source_topic_refs"])
    body = doc["body"]
    return (
        f"# {doc['title']}\n\n"
        f"- document_id: {doc['document_id']}\n"
        f"- version: {doc['version']}\n"
        f"- effective_at: {doc['effective_at']}\n"
        f"- division_id: {doc['division_id']}\n"
        f"- owner_employee_id: {doc['owner_employee_id']}\n"
        f"- security_scope: {doc['security_scope']}\n"
        f"- kind: {doc['kind']}\n"
        f"- world_model_id: wm_auroralis_v1\n"
        f"- generation_seed: {SEED}\n\n"
        f"## Source topic refs\n{refs}\n\n"
        f"## Body\n{body}\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-root", required=True, type=Path)
    args = parser.parse_args()

    out_root: Path = args.out_root
    corpus_root = out_root / "corpus"
    derived_root = out_root / "derived"
    corpus_root.mkdir(parents=True, exist_ok=True)
    derived_root.mkdir(parents=True, exist_ok=True)

    # Render corpus
    corpus_records = []
    for doc in DOCS:
        md = render_doc_markdown(doc)
        path = corpus_root / f"{doc['document_id']}.md"
        path.write_text(md, encoding="utf-8", newline="\n")
        corpus_records.append({
            "document_id": doc["document_id"],
            "title": doc["title"],
            "version": doc["version"],
            "effective_at": doc["effective_at"],
            "security_scope": doc["security_scope"],
            "kind": doc["kind"],
            "file_name": path.name,
            "sha256": _h(md.encode("utf-8")),
        })

    # world_model.json
    world = {
        "schema_version": "1.0.0",
        "world_model_id": "wm_auroralis_v1",
        "world_model_name": "Auroralis Manufacturing Group - Synthetic Enterprise World Model",
        "generation_seed": SEED,
        "generated_at_utc": GENERATION_TIME_UTC,
        "fictional_disclaimer": "All entities, roles, products, suppliers, contracts, policies, projects, events, versions, permissions, and timelines below are entirely fictional. No real companies, individuals, or web facts are referenced.",
        "company": COMPANY,
        "divisions": DIVISIONS,
        "ceo": CEO,
        "employees": EMPLOYEES,
        "products": PRODUCTS,
        "suppliers": SUPPLIERS,
        "contracts": CONTRACTS,
        "policies": POLICIES,
        "projects": PROJECTS,
        "events": EVENTS,
        "permissions": PERMISSIONS,
        "security_scopes": SECURITY_SCOPES,
        "documents": [
            {k: v for k, v in doc.items() if k != "body"} for doc in DOCS
        ],
        "relations": RELATIONS,
    }
    wm_bytes = json.dumps(world, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
    wm_path = out_root / "world_model.json"
    wm_path.write_bytes(wm_bytes)

    # corpus_manifest.json
    corpus_manifest = {
        "schema_version": "1.0.0",
        "corpus_id": "corpus_auroralis_v1",
        "world_model_id": "wm_auroralis_v1",
        "generation_seed": SEED,
        "generated_at_utc": GENERATION_TIME_UTC,
        "document_count": len(corpus_records),
        "documents": corpus_records,
    }
    cm_bytes = json.dumps(corpus_manifest, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
    cm_path = out_root / "corpus_manifest.json"
    cm_path.write_bytes(cm_bytes)

    # graph_manifest.json (deterministic, derived from relations)
    graph_manifest = {
        "schema_version": "1.0.0",
        "graph_id": "graph_auroralis_v1",
        "world_model_id": "wm_auroralis_v1",
        "generation_seed": SEED,
        "generated_at_utc": GENERATION_TIME_UTC,
        "node_count": (
            len(DIVISIONS) + len(EMPLOYEES) + 1  # CEO
            + len(PRODUCTS) + len(SUPPLIERS) + len(CONTRACTS) + len(POLICIES)
            + len(PROJECTS) + len(EVENTS) + len(PERMISSIONS) + 1  # company node
        ),
        "edge_count": len(RELATIONS),
        "relation_kinds": sorted({r["kind"] for r in RELATIONS}),
        "relations": RELATIONS,
    }
    gm_bytes = json.dumps(graph_manifest, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
    gm_path = out_root / "graph_manifest.json"
    gm_path.write_bytes(gm_bytes)

    # source_span_index.json — for each doc, capture which world entities are referenced
    # (entity ids appear as substrings in the body; for our deterministic corpus we
    # index by source_topic_refs membership + the security_scope reference).
    span_index = {}
    for doc in DOCS:
        spans = []
        for ref in doc["source_topic_refs"]:
            spans.append({
                "topic_ref": ref,
                "expected_text_substring": ref,
                "is_authoritative": True,
            })
        span_index[doc["document_id"]] = {
            "version": doc["version"],
            "effective_at": doc["effective_at"],
            "security_scope": doc["security_scope"],
            "source_spans": spans,
        }
    si_bytes = json.dumps(span_index, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")
    (derived_root / "source_span_index.json").write_bytes(si_bytes)

    # corpus_hashes.json
    hashes = {
        "world_model_sha256": _h(wm_bytes),
        "corpus_manifest_sha256": _h(cm_bytes),
        "graph_manifest_sha256": _h(gm_bytes),
        "source_span_index_sha256": _h(si_bytes),
        "document_hashes": {r["document_id"]: r["sha256"] for r in corpus_records},
    }
    (derived_root / "corpus_hashes.json").write_text(
        json.dumps(hashes, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    print(f"world_model_sha256={hashes['world_model_sha256']}")
    print(f"corpus_manifest_sha256={hashes['corpus_manifest_sha256']}")
    print(f"graph_manifest_sha256={hashes['graph_manifest_sha256']}")
    print(f"document_count={len(corpus_records)}")
    print(f"relation_count={len(RELATIONS)}")


if __name__ == "__main__":
    main()