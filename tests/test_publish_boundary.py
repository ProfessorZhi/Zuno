from pathlib import Path
import subprocess


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_gitignore_covers_private_and_local_surfaces() -> None:
    content = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")

    required_entries = [
        ".agent/",
        ".agentmd",
        ".local/",
        "docs/superpowers/",
        "apps/web/AGENTS.md",
        "infra/docker/docker_config.local.yaml",
        ".local/config/agentchat/",
        ".local/evals/agentchat/rag_eval/corpus/",
        ".local/evals/agentchat/rag_eval/runs/",
    ]

    for entry in required_entries:
        assert entry in content, f"missing publish-boundary ignore: {entry}"


def test_public_docs_link_current_architecture_and_publish_boundary() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    docs_index = (REPO_ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    dev_docs = (
        REPO_ROOT / "docs" / "development" / "README.md"
    ).read_text(encoding="utf-8")
    architecture_docs = (
        REPO_ROOT / "docs" / "architecture" / "README.md"
    ).read_text(encoding="utf-8")
    architecture_plans = (
        REPO_ROOT / "docs" / "architecture" / "plans" / "README.md"
    ).read_text(encoding="utf-8")
    architecture_phases = (
        REPO_ROOT / "docs" / "architecture" / "phases" / "README.md"
    ).read_text(encoding="utf-8")

    assert "./docs/development/github-publish-boundary.md" in readme
    assert "./docs/development/README.md" in readme
    assert "./docs/development/public-demo-runbook.md" in readme
    assert "./docs/development/public-demo-evidence.md" in readme
    assert "./docs/development/public-demo-acceptance.md" in readme
    assert "./docs/architecture/specs/enterprise-retrieval-governance.md" in readme
    assert "./docs/architecture/plans/retrieval-governance-upgrade-plan.md" in readme
    assert "python tools/scripts/verify_public_demo_runtime.py" in readme
    assert "python tools/scripts/verify_public_demo_strict_grounding.py" in readme
    assert "./docs/development/public-release-checklist.md" in readme
    assert "./docs/development/public-release-staging-plan.md" in readme
    assert "./development/github-publish-boundary.md" in docs_index
    assert "./development/architecture-doc-maintenance-workflow.md" in docs_index
    assert "architecture-doc-maintenance-workflow.md" in dev_docs
    assert "history/README.md" in dev_docs
    assert "public-release-checklist.md" in dev_docs
    assert "public-release-staging-plan.md" in dev_docs
    assert "public-demo-evidence.md" in dev_docs
    assert "public-demo-runbook.md" in dev_docs
    assert "public-demo-acceptance.md" in dev_docs
    assert "./specs/enterprise-retrieval-governance.md" in architecture_docs
    assert "./current-architecture.md" in architecture_docs
    assert "./target-architecture.md" in architecture_docs
    assert "./phases/README.md" in architecture_docs
    assert "./history/README.md" in architecture_docs
    assert "../phases/README.md" in architecture_plans
    assert "./retrieval-governance-upgrade-plan.md" in architecture_plans
    assert "Phase 1: Repo Skeleton" in architecture_phases
    assert "Phase 6: Public Surface" in architecture_phases


def test_public_indexes_do_not_present_local_superpowers_material_as_public_docs() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    docs_index = (REPO_ROOT / "docs" / "README.md").read_text(encoding="utf-8")

    forbidden_phrases = [
        "./superpowers/README.md",
        "└─ superpowers/",
    ]

    for phrase in forbidden_phrases:
        assert phrase not in readme, f"public README should not present excluded local docs: {phrase}"
        assert phrase not in docs_index, f"docs index should not present excluded local docs: {phrase}"


def test_public_readme_mentions_layered_and_future_architecture() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    required_phrases = [
        "Backend Control Layer",
        "Backend Service Layer",
        "Backend DAO Layer",
        "Infrastructure Layer",
        "多 agent 功能开发",
        "微服务与云原生部署演进",
        "Java 等非 Python 业务后端",
    ]

    for phrase in required_phrases:
        assert phrase in readme, f"missing public architecture direction: {phrase}"


def test_public_readme_mentions_demo_evidence() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    required_phrases = [
        "## Public Demo Evidence",
        "./docs/development/public-demo-evidence.md",
        "./docs/development/public-demo-acceptance.md",
        "Recall@5 `0.3167`",
        "MRR@5 `0.4000`",
        "Recall@5 `1.0000`",
        "MRR@5 `0.9583`",
        "NDCG@5 `0.9692`",
    ]

    for phrase in required_phrases:
        assert phrase in readme, f"missing public demo evidence phrase: {phrase}"


def test_public_docs_do_not_use_ignored_eval_run_paths_as_public_evidence() -> None:
    files = [
        REPO_ROOT / "README.md",
        REPO_ROOT / "docs" / "development" / "public-demo-runbook.md",
        REPO_ROOT / "docs" / "development" / "public-demo-acceptance.md",
        REPO_ROOT / "docs" / "architecture" / "current-architecture.md",
    ]

    forbidden_public_links = [
        "./src/backend/agentchat/evals/rag_eval/runs/",
        "/src/backend/agentchat/evals/rag_eval/runs/",
    ]

    for file in files:
        content = file.read_text(encoding="utf-8")
        for forbidden in forbidden_public_links:
            assert forbidden not in content, f"{file} should not link public evidence to ignored run outputs: {forbidden}"


def test_public_readme_explains_why_contract_review_needs_graphrag() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    required_phrases = [
        "## Why GraphRAG For Contract Review",
        "domain-modeling problem",
        "generic vector retrieval starts pulling many locally similar but structurally wrong distractors",
        "with larger and noisier corpora, typed extraction plus GraphRAG becomes much more valuable",
        "`contract_review` Domain Pack",
    ]

    for phrase in required_phrases:
        assert phrase in readme, f"missing contract-review GraphRAG explanation: {phrase}"


def test_public_docs_switch_to_new_architecture_upgrade_path() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    architecture_readme = (
        REPO_ROOT / "docs" / "architecture" / "README.md"
    ).read_text(encoding="utf-8")
    phase_index = (
        REPO_ROOT / "docs" / "architecture" / "phases" / "README.md"
    ).read_text(encoding="utf-8")

    assert "Current Architecture Upgrade Path" in readme
    assert "current-architecture.md" in readme
    assert "target-architecture.md" in readme
    assert "Architecture Upgrade Phases" in architecture_readme
    assert "Phase 1: Repo Skeleton" in phase_index
    assert "Phase 6: Public Surface" in phase_index

    forbidden_phrases = [
        "./plans/current-phase-audit.md",
        "./plans/zuno-refactor-execution-plan.md",
    ]

    for phrase in forbidden_phrases:
        assert phrase not in readme
        assert phrase not in architecture_readme


def test_current_architecture_upgrade_path_and_workflow_are_explicit() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    architecture_readme = (
        REPO_ROOT / "docs" / "architecture" / "README.md"
    ).read_text(encoding="utf-8")
    maintenance_workflow = (
        REPO_ROOT
        / "docs"
        / "development"
        / "architecture-doc-maintenance-workflow.md"
    ).read_text(encoding="utf-8")

    assert "Current Architecture Upgrade Path" in readme
    assert "Architecture Upgrade Phases" in architecture_readme
    for phrase in [
        "spec update",
        "active phase update",
        "targeted verification",
        "docs sync",
        "GitHub node",
    ]:
        assert phrase in maintenance_workflow, f"missing maintenance workflow phrase: {phrase}"


def test_architecture_and_development_history_keep_legacy_materials_reachable() -> None:
    architecture_history = (
        REPO_ROOT / "docs" / "architecture" / "history" / "README.md"
    ).read_text(encoding="utf-8")
    phase_index = (
        REPO_ROOT / "docs" / "architecture" / "phases" / "README.md"
    ).read_text(encoding="utf-8")
    development_history = (
        REPO_ROOT / "docs" / "development" / "history" / "README.md"
    ).read_text(encoding="utf-8")

    for phrase in [
        "historical phase context",
        "past readiness notes",
        "older refactor narratives",
    ]:
        assert phrase in architecture_history, f"missing architecture history phrase: {phrase}"

    for phrase in [
        "one-off signoff notes",
        "prestage checklists",
        "ready-check notes",
    ]:
        assert phrase in development_history, f"missing development history phrase: {phrase}"

    assert "Older `Phase 1-7` execution documents" in phase_index


def test_publish_boundary_doc_mentions_private_local_assets() -> None:
    content = (
        REPO_ROOT / "docs" / "development" / "github-publish-boundary.md"
    ).read_text(encoding="utf-8")

    required_phrases = [
        ".agent/",
        ".agentmd",
        ".local/",
        "docs/superpowers/",
        "apps/web/AGENTS.md",
        "docker_config.local.yaml",
        "config.local.yaml",
        "rag_eval/runs/",
        "rag_eval/corpus/",
        "public-release-checklist.md",
    ]

    for phrase in required_phrases:
        assert phrase in content, f"missing publish-boundary guidance: {phrase}"


def test_public_release_checklist_mentions_pre_push_audit_steps() -> None:
    content = (
        REPO_ROOT / "docs" / "development" / "public-release-checklist.md"
    ).read_text(encoding="utf-8")

    required_phrases = [
        ".agent/",
        ".agentmd",
        ".local/",
        "docs/superpowers/",
        "apps/web/AGENTS.md",
        "docker_config.local.yaml",
        "config.local.yaml",
        "rag_eval/runs/",
        "rag_eval/corpus/",
        "git status --short",
        "git diff --stat",
        "git diff --cached --stat",
        "python tools/scripts/summarize_public_release_scope.py",
        "python tools/scripts/preview_public_release_group.py docs_and_readme",
        "python tools/scripts/preview_public_release_group.py docs_and_readme --stat",
        "python tools/scripts/preview_public_release_stage_dry_run.py docs_and_readme",
        "python tools/scripts/verify_docs_and_readme_ready.py",
        "python tools/scripts/print_public_release_commit_order.py",
        "python tools/scripts/print_public_release_stage_commands.py",
        "tests/test_publish_boundary.py",
        "tests/test_zuno_public_entrypoints.py",
        "tests/test_zuno_runtime_chain_guard.py",
        "python tools/scripts/audit_public_release.py",
        "public-demo-evidence.md",
    ]

    for phrase in required_phrases:
        assert phrase in content, f"missing public release checklist guidance: {phrase}"


def test_public_release_audit_script_detects_ignored_eval_run_links() -> None:
    script = REPO_ROOT / "tools" / "scripts" / "audit_public_release.py"
    content = script.read_text(encoding="utf-8")

    assert "FORBIDDEN_PUBLIC_DOC_LINKS" in content
    assert "current-architecture.md" in content
    assert "git status --short" in content
    assert ".local/evals/agentchat/rag_eval/runs/" in content


def test_public_release_audit_script_runs_from_repo() -> None:
    script = REPO_ROOT / "tools" / "scripts" / "audit_public_release.py"

    proc = subprocess.run(
        ["python", str(script)],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    assert proc.returncode == 0 or proc.returncode == 1
    assert "Public release audit" in (proc.stdout + proc.stderr)


def test_public_demo_acceptance_doc_mentions_public_proof_gate() -> None:
    content = (
        REPO_ROOT / "docs" / "development" / "public-demo-acceptance.md"
    ).read_text(encoding="utf-8")

    required_phrases = [
        "public-proof acceptance layer",
        "real quality result for a public audience",
        "reproducible local command path",
        "why the answer or benchmark result holds",
        "Recall@5 `0.3167`",
        "MRR@5 `0.4000`",
        "Recall@5 `1.0000`",
        "MRR@5 `0.9583`",
        "NDCG@5 `0.9692`",
        "python tools/scripts/verify_public_demo_docs.py",
        "python tools/scripts/verify_public_demo_runtime.py",
        "python tools/scripts/verify_public_demo_strict_grounding.py",
        "NO_RELEVANT_EVIDENCE_FOUND",
    ]

    for phrase in required_phrases:
        assert phrase in content, f"missing public demo acceptance guidance: {phrase}"


def test_public_demo_verifier_script_mentions_expected_docs_and_metrics() -> None:
    script = (
        REPO_ROOT / "tools" / "scripts" / "verify_public_demo_docs.py"
    ).read_text(encoding="utf-8")

    required_phrases = [
        "README.md",
        "docs/development/README.md",
        "public-demo-runbook.md",
        "public-demo-evidence.md",
        "public-demo-acceptance.md",
        "verify_public_demo_runtime.py",
        "verify_public_demo_strict_grounding.py",
        "Recall@5 `0.3167`",
        "MRR@5 `0.4000`",
        "Recall@5 `1.0000`",
        "MRR@5 `0.9583`",
        "NDCG@5 `0.9692`",
        "public demo docs verification passed.",
    ]

    for phrase in required_phrases:
        assert phrase in script, f"missing public demo verifier rule: {phrase}"


def test_public_demo_runtime_verifier_script_mentions_contract_review_smoke_expectations() -> None:
    script = (
        REPO_ROOT / "tools" / "scripts" / "verify_public_demo_runtime.py"
    ).read_text(encoding="utf-8")

    required_phrases = [
        "run_contract_eval import run",
        'run("dev_offline", output_dir=report_root)',
        "Contract Review Report Template",
        "Clause -> CLAUSE_HAS_RISK",
        "citation_count",
        "path_count",
        "trace_node_count",
        "public demo runtime verification passed.",
    ]

    for phrase in required_phrases:
        assert phrase in script, f"missing public demo runtime verifier rule: {phrase}"


def test_public_demo_strict_grounding_verifier_script_mentions_supported_and_unsupported_cases() -> None:
    script = (
        REPO_ROOT / "tools" / "scripts" / "verify_public_demo_strict_grounding.py"
    ).read_text(encoding="utf-8")

    required_phrases = [
        "NO_EVIDENCE_ANSWER",
        "_build_answer",
        'answer_mode="strict_grounded"',
        "supported case should not degrade to NO_RELEVANT_EVIDENCE_FOUND",
        "unsupported case should degrade to NO_RELEVANT_EVIDENCE_FOUND",
        "public demo strict grounding verification passed.",
    ]

    for phrase in required_phrases:
        assert phrase in script, f"missing strict grounding verifier rule: {phrase}"


def test_public_release_staging_plan_mentions_grouping_rules() -> None:
    content = (
        REPO_ROOT / "docs" / "development" / "public-release-staging-plan.md"
    ).read_text(encoding="utf-8")

    required_phrases = [
        "tools/scripts/summarize_public_release_scope.py",
        "docs_and_readme",
        "tests_and_release_guards",
        "infra_and_launch",
        "backend_domain_runtime",
        "backend_rag_graphrag_eval",
        "backend_public_entrypoints",
        "frontend_workspace",
        "excluded_local_only",
        "manual_review",
        "public-release-checklist.md",
        "print_public_release_commit_order.py",
        "print_public_release_stage_commands.py",
        "preview_public_release_group.py",
        "preview_public_release_stage_dry_run.py",
        "verify_docs_and_readme_ready.py",
        "development/history/README.md",
    ]

    for phrase in required_phrases:
        assert phrase in content, f"missing public release staging plan guidance: {phrase}"


def test_public_release_scope_script_mentions_expected_groups() -> None:
    script = (
        REPO_ROOT / "tools" / "scripts" / "summarize_public_release_scope.py"
    ).read_text(encoding="utf-8")

    required_phrases = [
        "docs_and_readme",
        "infra_and_launch",
        "backend_domain_runtime",
        "backend_rag_graphrag_eval",
        "backend_public_entrypoints",
        "frontend_workspace",
        "tests_and_release_guards",
        "excluded_local_only",
        "docs/superpowers/",
        "apps/web/AGENTS.md",
        "manual_review",
        "preview_public_release_group.py",
        "git status --short",
    ]

    for phrase in required_phrases:
        assert phrase in script, f"missing release scope grouping rule: {phrase}"


def test_public_release_commit_order_script_mentions_review_boundaries() -> None:
    script = (
        REPO_ROOT / "tools" / "scripts" / "print_public_release_commit_order.py"
    ).read_text(encoding="utf-8")

    required_phrases = [
        "docs_and_readme",
        "tests_and_release_guards",
        "infra_and_launch",
        "backend_domain_runtime",
        "backend_rag_graphrag_eval",
        "backend_public_entrypoints",
        "frontend_workspace",
        "Excluded local-only content",
        "docs/superpowers/",
        "apps/web/AGENTS.md",
    ]

    for phrase in required_phrases:
        assert phrase in script, f"missing public release commit order rule: {phrase}"


def test_public_release_stage_commands_script_mentions_expected_groups() -> None:
    script = (
        REPO_ROOT / "tools" / "scripts" / "print_public_release_stage_commands.py"
    ).read_text(encoding="utf-8")

    required_phrases = [
        "docs_and_readme",
        "tests_and_release_guards",
        "infra_and_launch",
        "backend_domain_runtime",
        "backend_rag_graphrag_eval",
        "backend_public_entrypoints",
        "frontend_workspace",
        "docs/superpowers/",
        "apps/web/AGENTS.md",
        "git add README.md docs/",
    ]

    for phrase in required_phrases:
        assert phrase in script, f"missing public release stage command rule: {phrase}"


def test_public_release_group_preview_script_mentions_expected_groups() -> None:
    script = (
        REPO_ROOT / "tools" / "scripts" / "preview_public_release_group.py"
    ).read_text(encoding="utf-8")

    required_phrases = [
        "docs_and_readme",
        "infra_and_launch",
        "backend_domain_runtime",
        "backend_rag_graphrag_eval",
        "backend_public_entrypoints",
        "frontend_workspace",
        "tests_and_release_guards",
        "excluded_local_only",
        "manual_review",
        "\"docs_and_readme\"",
        "\"--stat\"",
        "git diff",
        "docs_and_readme",
    ]

    for phrase in required_phrases:
        assert phrase in script, f"missing public release preview rule: {phrase}"


def test_development_history_records_archived_workflow_temperature_docs() -> None:
    content = (
        REPO_ROOT / "docs" / "development" / "history" / "README.md"
    ).read_text(encoding="utf-8")

    required_phrases = [
        "one-off signoff notes",
        "prestage checklists",
        "ready-check notes",
        "architecture-doc-maintenance-workflow.md",
    ]

    for phrase in required_phrases:
        assert phrase in content, f"missing development history guidance: {phrase}"


def test_architecture_doc_maintenance_workflow_records_current_execution_steps() -> None:
    content = (
        REPO_ROOT / "docs" / "development" / "architecture-doc-maintenance-workflow.md"
    ).read_text(encoding="utf-8")

    required_phrases = [
        "spec update",
        "active phase update",
        "targeted verification",
        "docs sync",
        "GitHub node",
        "completed operational checklist",
    ]

    for phrase in required_phrases:
        assert phrase in content, f"missing architecture doc maintenance workflow guidance: {phrase}"


def test_public_release_stage_dry_run_script_mentions_expected_groups() -> None:
    script = (
        REPO_ROOT / "tools" / "scripts" / "preview_public_release_stage_dry_run.py"
    ).read_text(encoding="utf-8")

    required_phrases = [
        "docs_and_readme",
        "tests_and_release_guards",
        "infra_and_launch",
        "backend_domain_runtime",
        "backend_rag_graphrag_eval",
        "backend_public_entrypoints",
        "frontend_workspace",
        "git",
        "status",
        "--short",
        "docs_and_readme",
    ]

    for phrase in required_phrases:
        assert phrase in script, f"missing public release stage dry-run rule: {phrase}"


def test_development_readme_points_to_current_maintainer_workflow() -> None:
    content = (
        REPO_ROOT / "docs" / "development" / "README.md"
    ).read_text(encoding="utf-8")

    required_phrases = [
        "Architecture Doc Maintenance Workflow",
        "history/README.md",
        "public-release-checklist.md",
        "public-release-staging-plan.md",
    ]

    for phrase in required_phrases:
        assert phrase in content, f"missing development readme guidance: {phrase}"


def test_verify_docs_and_readme_ready_script_tracks_current_expected_paths() -> None:
    script = (
        REPO_ROOT / "tools" / "scripts" / "verify_docs_and_readme_ready.py"
    ).read_text(encoding="utf-8")

    required_phrases = [
        "EXPECTED_GROUP_PATHS",
        "docs/development/docs-and-readme-ready.md",
        "preview_public_release_group.py",
        "preview_public_release_stage_dry_run.py",
        "audit_public_release.py",
        "docs_and_readme readiness check passed.",
    ]

    for phrase in required_phrases:
        assert phrase in script, f"missing docs/readme ready verifier rule: {phrase}"
