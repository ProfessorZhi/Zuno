from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _read(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def _require_phrases(name: str, content: str, phrases: list[str]) -> list[str]:
    errors: list[str] = []
    for phrase in phrases:
        if phrase not in content:
            errors.append(f"{name} missing phrase: {phrase}")
    return errors


def main() -> int:
    readme = _read("README.md")
    dev_readme = _read("docs/development/README.md")
    runbook = _read("docs/development/public-demo-runbook.md")
    evidence = _read("docs/development/public-demo-evidence.md")
    acceptance = _read("docs/development/public-demo-acceptance.md")

    errors: list[str] = []

    errors.extend(
        _require_phrases(
            "README.md",
            readme,
            [
                "./docs/development/public-demo-runbook.md",
                "./docs/development/public-demo-evidence.md",
                "./docs/development/public-demo-acceptance.md",
                "python tools/scripts/verify_public_demo_runtime.py",
                "python tools/scripts/verify_public_demo_strict_grounding.py",
                "Recall@5 `0.3167`",
                "MRR@5 `0.4000`",
                "Recall@5 `1.0000`",
                "MRR@5 `0.9583`",
                "NDCG@5 `0.9692`",
                "## Why GraphRAG For Contract Review",
            ],
        )
    )

    errors.extend(
        _require_phrases(
            "docs/development/README.md",
            dev_readme,
            [
                "public-demo-evidence.md",
                "public-demo-runbook.md",
                "public-demo-acceptance.md",
                "public demo runtime smoke verification",
                "strict-grounded public demo smoke verification",
            ],
        )
    )

    errors.extend(
        _require_phrases(
            "public-demo-runbook.md",
            runbook,
            [
                "run_local_embedding_eval.py",
                "run_stackless_compare_matrix.py",
                "mixed_tuning_v2_graph_relation_small.jsonl",
                "contract_review_graph_relation_small.jsonl",
                "verify_public_demo_runtime.py",
                "verify_public_demo_strict_grounding.py",
                "Recall@5",
                "Hit Rate@5",
                "Context Precision@5",
                "MRR@5",
                "NDCG@5",
            ],
        )
    )

    errors.extend(
        _require_phrases(
            "public-demo-evidence.md",
            evidence,
            [
                "Generic Graph-Relation Benchmark",
                "Contract-Review Scaled Domain Benchmark",
                "`baseline_rag` | `0.1167` | `0.2000` | `0.1000`",
                "`rag_graph_chunk_backed` | `0.3167` | `0.4000` | `0.1667`",
                "`baseline_rag` | `0.3333` | `0.1486` | `0.1931` | `0.3333`",
                "`rag_graph_chunk_backed` | `1.0000` | `0.9583` | `0.9692` | `1.0000`",
            ],
        )
    )

    errors.extend(
        _require_phrases(
            "public-demo-acceptance.md",
            acceptance,
            [
                "public-proof acceptance layer",
                "real quality result for a public audience",
                "reproducible local command path",
                "why the answer or benchmark result holds",
                "python tools/scripts/verify_public_demo_docs.py",
                "python tools/scripts/verify_public_demo_runtime.py",
                "python tools/scripts/verify_public_demo_strict_grounding.py",
                "NO_RELEVANT_EVIDENCE_FOUND",
                "rag_eval/runs/",
            ],
        )
    )

    forbidden_public_links = [
        "./src/backend/agentchat/evals/rag_eval/runs/",
        "/src/backend/agentchat/evals/rag_eval/runs/",
    ]
    for forbidden in forbidden_public_links:
        if forbidden in readme or forbidden in runbook or forbidden in acceptance:
            errors.append(f"public demo docs still reference ignored local run output: {forbidden}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("public demo docs verification failed.")
        return 1

    print("public demo docs verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
