from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path
from typing import Any

BACKEND_ROOT = Path(__file__).resolve().parents[4] / "src" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from tools.evals.zuno.rag_eval.run_stackless_local_eval import run_stackless_local_eval
from tools.evals.zuno.rag_eval.paths import default_runs_root
from tools.evals.zuno.rag_eval.summarize_eval_profiles import summarize as summarize_profiles


PROFILE_SETS = {
    "local_compare": ["baseline_rag", "rag_rerank", "rag_graph_chunk_backed"],
    "graph_compare": ["baseline_rag", "rag_graph_chunk_backed", "rag_graph_chunk_backed_3hop"],
}


def _fmt(value: Any) -> str:
    return "-" if value is None else f"{float(value):.4f}"


def _build_dataset_coverage(*, dataset_path: Path, sample_limit: int | None) -> dict[str, Any]:
    samples: list[dict[str, Any]] = []
    with dataset_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            samples.append(json.loads(line))
            if sample_limit is not None and len(samples) >= sample_limit:
                break

    referenced_files: list[str] = []
    for sample in samples:
        for evidence in sample.get("gold_evidence") or []:
            file_name = evidence.get("file_contains")
            if file_name:
                referenced_files.append(str(file_name))

    unique_referenced_files = sorted(set(referenced_files))
    warning = None
    if len(samples) <= 3 or len(unique_referenced_files) <= 2:
        warning = (
            "Low coverage: this matrix run touches too few sampled questions or referenced files "
            "to support a strong GraphRAG-vs-RAG conclusion."
        )

    return {
        "sampled_question_count": len(samples),
        "unique_referenced_file_count": len(unique_referenced_files),
        "unique_referenced_files": unique_referenced_files,
        "warning": warning,
    }


def _build_slice_summaries(*, dataset_path: Path, output_root: Path, runs: dict[str, Any]) -> dict[str, Any]:
    slices: dict[str, Any] = {}
    for matrix_name in runs.keys():
        profiles_root = output_root / matrix_name
        slices[matrix_name] = summarize_profiles(dataset_path=dataset_path, profiles_root=profiles_root)
    return slices


def _metric_value(metrics: dict[str, Any], key: str) -> float | None:
    value = metrics.get(f"{key}_at_k")
    if value is not None:
        return float(value)
    value = metrics.get(key)
    if value is not None:
        return float(value)
    return None


def _build_acceptance(summary: dict[str, Any]) -> dict[str, Any]:
    slices = summary.get("slices") or {}
    graph_compare = ((slices.get("graph_compare") or {}).get("profiles") or {})
    local_compare = ((slices.get("local_compare") or {}).get("profiles") or {})

    baseline_graph = (graph_compare.get("baseline_rag") or {}).get("graph_relation") or {}
    graph_2hop = (graph_compare.get("rag_graph_chunk_backed") or {}).get("graph_relation") or {}
    graph_3hop = (graph_compare.get("rag_graph_chunk_backed_3hop") or {}).get("graph_relation") or {}
    rerank_local = (local_compare.get("rag_rerank") or {}).get("graph_relation") or {}
    graph_local = (local_compare.get("rag_graph_chunk_backed") or {}).get("graph_relation") or {}

    baseline_recall = _metric_value(baseline_graph, "retrieval_recall")
    baseline_mrr = _metric_value(baseline_graph, "mrr")
    graph_2hop_recall = _metric_value(graph_2hop, "retrieval_recall")
    graph_2hop_mrr = _metric_value(graph_2hop, "mrr")
    graph_2hop_citation = _metric_value(graph_2hop, "citation_accuracy")
    baseline_citation = _metric_value(baseline_graph, "citation_accuracy")
    graph_3hop_recall = _metric_value(graph_3hop, "retrieval_recall")
    graph_3hop_precision = _metric_value(graph_3hop, "context_precision")
    graph_2hop_precision = _metric_value(graph_2hop, "context_precision")
    rerank_recall = _metric_value(rerank_local, "retrieval_recall")
    rerank_mrr = _metric_value(rerank_local, "mrr")
    graph_local_recall = _metric_value(graph_local, "retrieval_recall")
    graph_local_mrr = _metric_value(graph_local, "mrr")

    gates = {
        "graph_relation_2hop_not_worse_than_baseline": {
            "passed": (
                baseline_recall is not None
                and baseline_mrr is not None
                and graph_2hop_recall is not None
                and graph_2hop_mrr is not None
                and graph_2hop_recall >= baseline_recall
                and graph_2hop_mrr >= baseline_mrr
            ),
            "details": {
                "baseline_recall": baseline_recall,
                "baseline_mrr": baseline_mrr,
                "graph_2hop_recall": graph_2hop_recall,
                "graph_2hop_mrr": graph_2hop_mrr,
            },
        },
        "graph_relation_citation_not_lower_than_baseline": {
            "passed": (
                baseline_citation is not None
                and graph_2hop_citation is not None
                and graph_2hop_citation >= baseline_citation
            ),
            "details": {
                "baseline_citation_accuracy": baseline_citation,
                "graph_2hop_citation_accuracy": graph_2hop_citation,
            },
        },
        "three_hop_only_if_precision_not_hurt": {
            "passed": not (
                graph_3hop_recall is not None
                and graph_2hop_recall is not None
                and graph_3hop_precision is not None
                and graph_2hop_precision is not None
                and graph_3hop_recall > graph_2hop_recall
                and graph_3hop_precision < graph_2hop_precision
            ),
            "details": {
                "graph_2hop_recall": graph_2hop_recall,
                "graph_3hop_recall": graph_3hop_recall,
                "graph_2hop_context_precision": graph_2hop_precision,
                "graph_3hop_context_precision": graph_3hop_precision,
            },
        },
        "prefer_rerank_when_tied": {
            "passed": not (
                rerank_recall is not None
                and rerank_mrr is not None
                and graph_local_recall is not None
                and graph_local_mrr is not None
                and abs(rerank_recall - graph_local_recall) < 1e-9
                and abs(rerank_mrr - graph_local_mrr) < 1e-9
            ),
            "details": {
                "rerank_recall": rerank_recall,
                "rerank_mrr": rerank_mrr,
                "graph_local_recall": graph_local_recall,
                "graph_local_mrr": graph_local_mrr,
            },
            "note": "If this gate is false, keep rag_rerank as the safer default and treat GraphRAG as specialized.",
        },
    }
    return gates


async def run_matrix(
    *,
    manifest_path: Path,
    dataset_path: Path,
    output_root: Path,
    sample_limit: int | None = None,
    local_compare_rerank_threshold_override: float | None = None,
    graph_compare_rerank_threshold_override: float | None = None,
    domain_pack_id: str | None = None,
    chunk_size_override: int | None = None,
    overlap_override: int | None = None,
) -> dict[str, Any]:
    output_root.mkdir(parents=True, exist_ok=True)
    runs: dict[str, Any] = {}
    coverage = _build_dataset_coverage(dataset_path=dataset_path, sample_limit=sample_limit)

    local_compare_dir = output_root / "local_compare"
    runs["local_compare"] = await run_stackless_local_eval(
        manifest_path=manifest_path,
        dataset_path=dataset_path,
        output_root=local_compare_dir,
        profile_set="local_compare",
        sample_limit=sample_limit,
        spawn_dev_embedding_server=True,
        spawn_dev_rerank_server=True,
        rerank_score_threshold_override=local_compare_rerank_threshold_override,
        domain_pack_id=domain_pack_id,
        chunk_size_override=chunk_size_override,
        overlap_override=overlap_override,
    )

    graph_compare_dir = output_root / "graph_compare"
    runs["graph_compare"] = await run_stackless_local_eval(
        manifest_path=manifest_path,
        dataset_path=dataset_path,
        output_root=graph_compare_dir,
        profile_set="graph_compare",
        sample_limit=sample_limit,
        spawn_dev_embedding_server=True,
        spawn_dev_rerank_server=False,
        rerank_score_threshold_override=graph_compare_rerank_threshold_override,
        domain_pack_id=domain_pack_id,
        chunk_size_override=chunk_size_override,
        overlap_override=overlap_override,
    )

    return {
        "manifest_path": str(manifest_path),
        "dataset_path": str(dataset_path),
        "sample_limit": sample_limit,
        "domain_pack_id": domain_pack_id,
        "chunk_size_override": chunk_size_override,
        "overlap_override": overlap_override,
        "coverage": coverage,
        "runs": {
            matrix_name: {
                "profiles": result["profiles"],
                "knowledge_id": result["knowledge_id"],
                "chunk_count": result["chunk_count"],
                "output_root": result["output_root"],
                "rerank_score_threshold_override": result.get("rerank_score_threshold_override"),
                "report": result["report"],
            }
            for matrix_name, result in runs.items()
        },
        "slices": _build_slice_summaries(dataset_path=dataset_path, output_root=output_root, runs=runs),
        "acceptance": {},
    }


def write_markdown(path: Path, matrix_summary: dict[str, Any]) -> None:
    lines = [
        "# Zuno Stackless Compare Matrix",
        "",
        f"- Dataset: `{matrix_summary['dataset_path']}`",
        f"- Manifest: `{matrix_summary['manifest_path']}`",
        f"- Sample Limit: `{matrix_summary.get('sample_limit')}`",
        "",
    ]
    coverage = matrix_summary.get("coverage") or {}
    if coverage:
        lines.extend(
            [
                "## Coverage",
                "",
                f"- Sampled Questions: `{coverage.get('sampled_question_count')}`",
                f"- Unique Referenced Files: `{coverage.get('unique_referenced_file_count')}`",
            ]
        )
        warning = coverage.get("warning")
        if warning:
            lines.append(f"- Warning: {warning}")
        files = coverage.get("unique_referenced_files") or []
        if files:
            lines.append(f"- Referenced Files: `{', '.join(files)}`")
        lines.append("")
    for matrix_name, result in matrix_summary["runs"].items():
        lines.extend(
            [
                f"## {matrix_name}",
                "",
                f"- Output: `{result['output_root']}`",
                f"- Profiles: `{', '.join(result['profiles'])}`",
                f"- Rerank Threshold Override: `{result.get('rerank_score_threshold_override')}`",
                f"- Chunk Count: `{result.get('chunk_count')}`",
                "",
                "| Profile | Recall@5 | Hit Rate@5 | Context Precision@5 | MRR@5 | NDCG@5 | Faithfulness | Citation Accuracy |",
                "|---|---:|---:|---:|---:|---:|---:|---:|",
            ]
        )
        for profile, metrics in result["report"]["profiles"].items():
            lines.append(
                f"| {profile} | {_fmt(metrics.get('retrieval_recall_at_k'))} | {_fmt(metrics.get('hit_rate_at_k'))} | "
                f"{_fmt(metrics.get('context_precision_at_k'))} | {_fmt(metrics.get('mrr_at_k'))} | "
                f"{_fmt(metrics.get('ndcg_at_k'))} | {_fmt(metrics.get('faithfulness'))} | "
                f"{_fmt(metrics.get('citation_accuracy'))} |"
            )
        lines.append("")
        slice_summary = (matrix_summary.get("slices") or {}).get(matrix_name) or {}
        profiles = slice_summary.get("profiles") or {}
        if profiles:
            lines.extend(
                [
                    f"### {matrix_name} graph_relation",
                    "",
                    "| Profile | Samples | Recall@5 | Context Precision@5 | MRR@5 | NDCG@5 | Citation Accuracy |",
                    "|---|---:|---:|---:|---:|---:|---:|",
                ]
            )
            for profile in result["profiles"]:
                graph = (profiles.get(profile) or {}).get("graph_relation") or {}
                lines.append(
                    f"| {profile} | {graph.get('sample_count', 0)} | "
                    f"{_fmt(graph.get('retrieval_recall_at_k') or graph.get('retrieval_recall'))} | "
                    f"{_fmt(graph.get('context_precision_at_k') or graph.get('context_precision'))} | "
                    f"{_fmt(graph.get('mrr_at_k') or graph.get('mrr'))} | "
                    f"{_fmt(graph.get('ndcg_at_k') or graph.get('ndcg'))} | "
                    f"{_fmt(graph.get('citation_accuracy'))} |"
                )
            lines.append("")
    acceptance = matrix_summary.get("acceptance") or {}
    if acceptance:
        lines.extend(
            [
                "## Acceptance",
                "",
                "| Gate | Passed |",
                "|---|---|",
            ]
        )
        for gate_name, gate in acceptance.items():
            lines.append(f"| {gate_name} | {'yes' if gate.get('passed') else 'no'} |")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run stackless local_compare + graph_compare matrix.")
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--output-root", type=Path, default=None)
    parser.add_argument("--sample-limit", type=int, default=None)
    parser.add_argument("--local-compare-rerank-threshold-override", type=float, default=0.0)
    parser.add_argument("--graph-compare-rerank-threshold-override", type=float, default=None)
    parser.add_argument("--domain-pack-id", default=None)
    parser.add_argument("--chunk-size-override", type=int, default=None)
    parser.add_argument("--overlap-override", type=int, default=None)
    args = parser.parse_args()

    output_root = args.output_root or default_runs_root() / f"stackless-compare-matrix-{time.strftime('%Y%m%d-%H%M%S')}"
    summary = asyncio.run(
        run_matrix(
            manifest_path=args.manifest,
            dataset_path=args.dataset,
            output_root=output_root,
            sample_limit=args.sample_limit,
            local_compare_rerank_threshold_override=args.local_compare_rerank_threshold_override,
            graph_compare_rerank_threshold_override=args.graph_compare_rerank_threshold_override,
            domain_pack_id=args.domain_pack_id,
            chunk_size_override=args.chunk_size_override,
            overlap_override=args.overlap_override,
        )
    )
    summary["acceptance"] = _build_acceptance(summary)
    (output_root / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(output_root / "summary.md", summary)
    print(json.dumps({"output_root": str(output_root), "matrices": list(summary["runs"].keys())}, ensure_ascii=False))


if __name__ == "__main__":
    main()
