from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _index_by_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(row.get("id") or ""): row for row in rows if str(row.get("id") or "")}


def _safe_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _profile_snapshot(profile_dir: Path) -> dict[str, dict[str, Any]]:
    judges = _index_by_id(_load_jsonl(profile_dir / "judge_results.jsonl"))
    retrieval = _index_by_id(_load_jsonl(profile_dir / "retrieval_results.jsonl"))
    answers = _index_by_id(_load_jsonl(profile_dir / "answers.jsonl"))

    snapshots: dict[str, dict[str, Any]] = {}
    for sample_id in sorted(set(judges) | set(retrieval) | set(answers)):
        judge = judges.get(sample_id) or {}
        result = retrieval.get(sample_id) or {}
        answer = answers.get(sample_id) or {}
        metadata = result.get("metadata") or {}
        rounds = metadata.get("rounds") or []
        first_round = rounds[0] if rounds else {}
        contexts = result.get("contexts") or []
        snapshots[sample_id] = {
            "answer_correctness": _safe_float(judge.get("answer_correctness")),
            "faithfulness": _safe_float(judge.get("faithfulness")),
            "citation_count": len(answer.get("citations") or []),
            "context_count": len(contexts),
            "path_count": int(first_round.get("path_count") or 0),
            "entity_count": int(first_round.get("entity_count") or 0),
            "top_sources": [str(ctx.get("file_name") or ctx.get("source") or "") for ctx in contexts[:3]],
            "answer": str(answer.get("answer") or "").strip(),
        }
    return snapshots


def analyze_profiles(*, dataset_path: Path, profiles_root: Path, profiles: list[str]) -> dict[str, Any]:
    dataset_rows = _index_by_id(_load_jsonl(dataset_path))
    snapshots = {profile: _profile_snapshot(profiles_root / profile) for profile in profiles}

    rows: list[dict[str, Any]] = []
    for sample_id, sample in dataset_rows.items():
        profile_rows = {profile: snapshots.get(profile, {}).get(sample_id, {}) for profile in profiles}
        baseline = profile_rows.get("baseline_rag", {})
        rerank = profile_rows.get("rag_rerank", {})
        graph = profile_rows.get("rag_graph_chunk_backed", {})
        rows.append(
            {
                "id": sample_id,
                "question_type": sample.get("question_type"),
                "query": sample.get("query"),
                "baseline_answer_correctness": _safe_float(baseline.get("answer_correctness")),
                "rerank_answer_correctness": _safe_float(rerank.get("answer_correctness")),
                "graph_answer_correctness": _safe_float(graph.get("answer_correctness")),
                "graph_minus_baseline": _safe_float(graph.get("answer_correctness")) - _safe_float(baseline.get("answer_correctness")),
                "graph_minus_rerank": _safe_float(graph.get("answer_correctness")) - _safe_float(rerank.get("answer_correctness")),
                "graph_path_count": int(graph.get("path_count") or 0),
                "graph_entity_count": int(graph.get("entity_count") or 0),
                "baseline_top_sources": baseline.get("top_sources") or [],
                "graph_top_sources": graph.get("top_sources") or [],
            }
        )

    wins_vs_baseline = sum(1 for row in rows if row["graph_minus_baseline"] > 0)
    wins_vs_rerank = sum(1 for row in rows if row["graph_minus_rerank"] > 0)
    zero_path_samples = [row["id"] for row in rows if row["graph_path_count"] <= 0]
    return {
        "dataset_path": str(dataset_path),
        "profiles_root": str(profiles_root),
        "profiles": profiles,
        "wins_vs_baseline": wins_vs_baseline,
        "wins_vs_rerank": wins_vs_rerank,
        "zero_path_samples": zero_path_samples,
        "rows": rows,
    }


def write_report(analysis: dict[str, Any], output_path: Path) -> None:
    lines = [
        "# Profile Delta Analysis",
        "",
        f"- Dataset: `{analysis['dataset_path']}`",
        f"- Profiles Root: `{analysis['profiles_root']}`",
        f"- Wins Vs Baseline: `{analysis['wins_vs_baseline']}`",
        f"- Wins Vs Rerank: `{analysis['wins_vs_rerank']}`",
        f"- Zero Path Samples: `{', '.join(analysis['zero_path_samples']) or 'none'}`",
        "",
        "| ID | Type | Graph-Baseline | Graph-Rerank | Graph Paths | Graph Entities |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in analysis["rows"]:
        lines.append(
            f"| {row['id']} | {row['question_type']} | {row['graph_minus_baseline']:.4f} | "
            f"{row['graph_minus_rerank']:.4f} | {row['graph_path_count']} | {row['graph_entity_count']} |"
        )
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze per-sample deltas between baseline, rerank, and graph profiles.")
    parser.add_argument("--dataset", type=Path, required=True)
    parser.add_argument("--profiles-root", type=Path, required=True)
    parser.add_argument(
        "--profiles",
        default="baseline_rag,rag_rerank,rag_graph_chunk_backed",
        help="Comma-separated profile names under profiles-root.",
    )
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-md", type=Path, required=True)
    args = parser.parse_args()

    profiles = [item.strip() for item in str(args.profiles).split(",") if item.strip()]
    analysis = analyze_profiles(dataset_path=args.dataset, profiles_root=args.profiles_root, profiles=profiles)
    args.output_json.write_text(json.dumps(analysis, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(analysis, args.output_md)
    print(
        json.dumps(
            {
                "output_json": str(args.output_json),
                "output_md": str(args.output_md),
                "wins_vs_baseline": analysis["wins_vs_baseline"],
                "wins_vs_rerank": analysis["wins_vs_rerank"],
                "zero_path_samples": analysis["zero_path_samples"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
