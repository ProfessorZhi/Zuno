from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable


METRICS = [
    "retrieval_recall",
    "hit_rate",
    "context_precision",
    "mrr",
    "ndcg",
    "faithfulness",
    "answer_correctness",
    "citation_accuracy",
]


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            text = line.strip()
            if text:
                rows.append(json.loads(text))
    return rows


def _mean(values: Iterable[float | None]) -> float | None:
    usable = [value for value in values if value is not None]
    if not usable:
        return None
    return sum(usable) / len(usable)


def _fmt(value: Any) -> str:
    return "-" if value is None else f"{float(value):.4f}"


def _aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {"sample_count": len(rows)}
    for metric in METRICS:
        result[metric] = _mean(row.get(metric) for row in rows)
    return result


def _profile_name(profile_dir: Path, metrics: dict[str, Any]) -> str:
    profiles = list(((profile_dir / "report.json").exists() and json.loads((profile_dir / "report.json").read_text(encoding="utf-8")).get("profiles") or {}).keys())
    return profiles[0] if profiles else profile_dir.name


def summarize(*, dataset_path: Path, profiles_root: Path) -> dict[str, Any]:
    samples = {sample["id"]: sample for sample in _read_jsonl(dataset_path)}
    profile_summaries: dict[str, Any] = {}

    for metrics_path in sorted(profiles_root.glob("*/**/metrics.json")):
        profile_dir = metrics_path.parent
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        profile = profile_dir.name

        enriched = []
        for row in metrics.get("per_sample") or []:
            sample = samples.get(row["id"], {})
            enriched.append(
                {
                    **row,
                    "question_type": sample.get("question_type", "unknown"),
                    "category": sample.get("category", "unknown"),
                    "is_graph_relation": bool(sample.get("is_graph_relation")),
                }
            )

        by_question_type: dict[str, Any] = {}
        for question_type in sorted({row["question_type"] for row in enriched}):
            by_question_type[question_type] = _aggregate(
                [row for row in enriched if row["question_type"] == question_type]
            )

        graph_relation_rows = [row for row in enriched if row["is_graph_relation"]]
        profile_summaries[profile] = {
            "overall": metrics.get("aggregate") or _aggregate(enriched),
            "by_question_type": by_question_type,
            "graph_relation": _aggregate(graph_relation_rows),
        }

    return {
        "dataset": str(dataset_path),
        "profiles_root": str(profiles_root),
        "profiles": profile_summaries,
    }


def write_markdown(path: Path, summary: dict[str, Any]) -> None:
    lines = [
        "# Zuno Mixed Tuning V2 Profile Summary",
        "",
        "## Overall",
        "",
        "| Profile | Recall@5 | Context Precision@5 | MRR@5 | NDCG@5 | Faithfulness | Answer Correctness | Citation Accuracy |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for profile, profile_summary in summary["profiles"].items():
        overall = profile_summary["overall"]
        lines.append(
            f"| {profile} | {_fmt(overall.get('retrieval_recall_at_k') or overall.get('retrieval_recall'))} | "
            f"{_fmt(overall.get('context_precision_at_k') or overall.get('context_precision'))} | "
            f"{_fmt(overall.get('mrr_at_k') or overall.get('mrr'))} | "
            f"{_fmt(overall.get('ndcg_at_k') or overall.get('ndcg'))} | "
            f"{_fmt(overall.get('faithfulness'))} | {_fmt(overall.get('answer_correctness'))} | "
            f"{_fmt(overall.get('citation_accuracy'))} |"
        )

    lines.extend(
        [
            "",
            "## Graph Relation",
            "",
            "| Profile | Samples | Recall@5 | Context Precision@5 | MRR@5 | NDCG@5 | Citation Accuracy |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for profile, profile_summary in summary["profiles"].items():
        graph = profile_summary["graph_relation"]
        lines.append(
            f"| {profile} | {graph.get('sample_count')} | {_fmt(graph.get('retrieval_recall'))} | "
            f"{_fmt(graph.get('context_precision'))} | {_fmt(graph.get('mrr'))} | "
            f"{_fmt(graph.get('ndcg'))} | {_fmt(graph.get('citation_accuracy'))} |"
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize multiple Zuno rag_eval profile runs.")
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--profiles-root", required=True, type=Path)
    parser.add_argument("--output-json", required=True, type=Path)
    parser.add_argument("--output-md", required=True, type=Path)
    args = parser.parse_args()

    summary = summarize(dataset_path=args.dataset, profiles_root=args.profiles_root)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(args.output_md, summary)
    print(json.dumps({"profiles": list(summary["profiles"].keys()), "output": str(args.output_json)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
