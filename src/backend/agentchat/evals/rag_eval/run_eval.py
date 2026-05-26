from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Awaitable, Callable

BACKEND_ROOT = Path(__file__).resolve().parents[3]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from agentchat.evals.rag_eval.metrics import compute_metrics
from agentchat.services.rag.handler import RagHandler
from agentchat.settings import initialize_app_settings
from agentchat.utils.runtime_observability import configure_langsmith

NO_EVIDENCE_ANSWER = "NO_RELEVANT_EVIDENCE_FOUND"

PROFILE_SETTINGS: dict[str, dict[str, Any]] = {
    "baseline_rag": {
        "retrieval_mode": "rag",
        "retrieval_options": {
            "top_k": 5,
            "rerank_enabled": False,
            "rerank_top_k": 5,
            "score_threshold": None,
            "needs_query_rewrite": False,
        },
    },
    "rag_rerank": {
        "retrieval_mode": "rag",
        "retrieval_options": {
            "top_k": 5,
            "rerank_enabled": True,
            "rerank_top_k": 3,
            "score_threshold": 0.7,
            "needs_query_rewrite": True,
        },
    },
    "parent_child_rag": {
        "retrieval_mode": "rag",
        "retrieval_options": {
            "top_k": 5,
            "rerank_enabled": True,
            "rerank_top_k": 3,
            "score_threshold": 0.7,
            "needs_query_rewrite": True,
        },
    },
    "rag_graph": {
        "retrieval_mode": "rag_graph",
        "retrieval_options": {
            "top_k": 5,
            "rerank_enabled": True,
            "rerank_top_k": 3,
            "score_threshold": 0.7,
            "graph_hop_limit": 2,
            "max_paths_per_entity": 5,
            "needs_query_rewrite": True,
        },
    },
    "rag_graph_3hop": {
        "retrieval_mode": "rag_graph",
        "retrieval_options": {
            "top_k": 5,
            "rerank_enabled": True,
            "rerank_top_k": 3,
            "score_threshold": 0.7,
            "graph_hop_limit": 3,
            "max_paths_per_entity": 10,
            "needs_query_rewrite": True,
        },
    },
}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as file:
        for line in file:
            text = line.strip()
            if text:
                rows.append(json.loads(text))
    return rows


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(json.dumps(row, ensure_ascii=False) for row in rows) + ("\n" if rows else ""),
        encoding="utf-8",
    )


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[\w\u4e00-\u9fff]+", str(text or "").lower()))


def _overlap_score(answer: str, reference: str) -> float:
    answer_tokens = _tokenize(answer)
    reference_tokens = _tokenize(reference)
    if not reference_tokens:
        return 1.0
    if not answer_tokens:
        return 0.0
    return len(answer_tokens & reference_tokens) / len(reference_tokens)


def _extract_contexts(retrieval_result: dict[str, Any]) -> list[dict[str, Any]]:
    rag_result = retrieval_result.get("rag_result") or {}
    documents = list(rag_result.get("documents") or [])
    graph_result = retrieval_result.get("graph_result") or {}
    for path in graph_result.get("paths") or []:
        documents.append(
            {
                "content": str(path),
                "source": "Neo4j GraphRAG",
                "score": None,
                "kind": "graph_path",
            }
        )
    return documents


def _build_answer(sample: dict[str, Any], contexts: list[dict[str, Any]]) -> dict[str, Any]:
    context_text = "\n".join(str(context.get("content", "")) for context in contexts[:3]).strip()
    if context_text:
        answer = context_text[:1200]
    else:
        answer = NO_EVIDENCE_ANSWER
    return {
        "id": sample["id"],
        "query": sample["query"],
        "answer": answer,
        "citations": contexts[:3],
    }


def _judge_answer(sample: dict[str, Any], answer_row: dict[str, Any], contexts: list[dict[str, Any]]) -> dict[str, Any]:
    answer = str(answer_row.get("answer") or "")
    context_text = "\n".join(str(context.get("content", "")) for context in contexts)
    reference = str(sample.get("reference_answer") or "")
    return {
        "id": sample["id"],
        "faithfulness": 1.0 if answer and answer != NO_EVIDENCE_ANSWER and answer in context_text else 0.0,
        "answer_correctness": _overlap_score(answer, reference),
    }


def _fmt(value: Any) -> str:
    return "-" if value is None else f"{float(value):.4f}"


def _write_markdown_report(path: Path, profile_reports: dict[str, Any]) -> None:
    lines = [
        "# Zuno RAG Evaluation Report",
        "",
        "| Profile | Recall@5 | Context Precision@5 | Faithfulness | Answer Correctness | Citation Accuracy |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for profile, metrics in profile_reports.items():
        lines.append(
            "| {profile} | {recall} | {precision} | {faithfulness} | {correctness} | {citation} |".format(
                profile=profile,
                recall=_fmt(metrics.get("retrieval_recall_at_k")),
                precision=_fmt(metrics.get("context_precision_at_k")),
                faithfulness=_fmt(metrics.get("faithfulness")),
                correctness=_fmt(metrics.get("answer_correctness")),
                citation=_fmt(metrics.get("citation_accuracy")),
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


async def _maybe_trace(
    *,
    enabled: bool,
    run_name: str,
    metadata: dict[str, Any],
    func: Callable[[], Awaitable[dict[str, Any]]],
) -> dict[str, Any]:
    if not enabled:
        return await func()

    try:
        from langsmith import traceable
    except Exception:
        return await func()

    traced = traceable(name=run_name, run_type="chain", metadata=metadata)(func)
    return await traced()


async def run_eval(
    *,
    dataset_path: Path,
    knowledge_ids: list[str],
    profiles: list[str],
    output_dir: Path,
    trace_langsmith: bool = False,
) -> dict[str, Any]:
    await initialize_app_settings()
    if trace_langsmith:
        configure_langsmith()

    samples = _read_jsonl(dataset_path)
    output_dir.mkdir(parents=True, exist_ok=True)
    config_path = output_dir / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "dataset": str(dataset_path),
                "knowledge_ids": knowledge_ids,
                "profiles": profiles,
                "profile_settings": {
                    profile: PROFILE_SETTINGS.get(profile, {})
                    for profile in profiles
                },
                "trace_langsmith": trace_langsmith,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    profile_reports: dict[str, Any] = {}
    for profile in profiles:
        profile_settings = PROFILE_SETTINGS.get(
            profile,
            {
                "retrieval_mode": "rag_graph" if "graph" in profile else "rag",
                "retrieval_options": {},
            },
        )
        profile_dir = output_dir / profile
        retrieval_rows: list[dict[str, Any]] = []
        answer_rows: list[dict[str, Any]] = []
        judge_rows: list[dict[str, Any]] = []

        retrieval_mode = profile_settings["retrieval_mode"]
        retrieval_options = dict(profile_settings.get("retrieval_options") or {})
        for sample in samples:
            metadata = {
                "eval_run_id": output_dir.name,
                "eval_sample_id": sample["id"],
                "profile_name": profile,
                "retrieval_mode": retrieval_mode,
                "retrieval_options": retrieval_options,
                "knowledge_ids": knowledge_ids,
            }

            async def retrieve_one() -> dict[str, Any]:
                return await RagHandler.retrieve_ranked_documents_with_metadata(
                    sample["query"],
                    knowledge_ids,
                    knowledge_ids,
                    retrieval_mode=retrieval_mode,
                    retrieval_options=retrieval_options,
                )

            retrieval_result = await _maybe_trace(
                enabled=trace_langsmith,
                run_name=f"zuno-rag-eval:{profile}:{sample['id']}",
                metadata=metadata,
                func=retrieve_one,
            )
            contexts = _extract_contexts(retrieval_result)
            retrieval_rows.append(
                {
                    "id": sample["id"],
                    "query": sample["query"],
                    "profile": profile,
                    "retrieval_mode": retrieval_mode,
                    "retrieval_options": retrieval_options,
                    "contexts": contexts,
                    "metadata": retrieval_result.get("metadata") or {},
                    "raw_result": {
                        "first_mode": retrieval_result.get("first_mode"),
                        "final_mode": retrieval_result.get("final_mode"),
                        "fallback_reason": retrieval_result.get("fallback_reason"),
                        "round_count": retrieval_result.get("round_count"),
                    },
                }
            )

            answer_row = _build_answer(sample, contexts)
            answer_rows.append(answer_row)
            judge_rows.append(_judge_answer(sample, answer_row, contexts))

        retrieval_path = profile_dir / "retrieval_results.jsonl"
        answers_path = profile_dir / "answers.jsonl"
        judges_path = profile_dir / "judge_results.jsonl"
        metrics_path = profile_dir / "metrics.json"
        _write_jsonl(retrieval_path, retrieval_rows)
        _write_jsonl(answers_path, answer_rows)
        _write_jsonl(judges_path, judge_rows)

        metrics = compute_metrics(
            dataset_path=dataset_path,
            retrieval_results_path=retrieval_path,
            answers_path=answers_path,
            judge_results_path=judges_path,
            k=5,
        )
        metrics_path.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
        profile_reports[profile] = metrics["aggregate"]

    report = {
        "output_dir": str(output_dir),
        "profiles": profile_reports,
    }
    (output_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    _write_markdown_report(output_dir / "report.md", profile_reports)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Zuno RAG evaluation profiles.")
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--knowledge-id", action="append", dest="knowledge_ids", required=True)
    parser.add_argument("--profiles", default="baseline_rag,rag_rerank,rag_graph")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--trace-langsmith", action="store_true")
    args = parser.parse_args()

    output_dir = args.output_dir or Path("src/backend/agentchat/evals/rag_eval/runs") / time.strftime("%Y%m%d-%H%M%S")
    report = asyncio.run(
        run_eval(
            dataset_path=args.dataset,
            knowledge_ids=args.knowledge_ids,
            profiles=[profile.strip() for profile in args.profiles.split(",") if profile.strip()],
            output_dir=output_dir,
            trace_langsmith=args.trace_langsmith,
        )
    )
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
