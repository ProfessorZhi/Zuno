from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[4]
SAMPLE_ROOT = REPO_ROOT / "tools" / "evals" / "zuno" / "multihop_eval" / "sample_data"
DEFAULT_OUTPUT_ROOT = REPO_ROOT / "reports" / "evals" / "multihop"

SUPPORTED_MODES = {"baseline_rag", "local_graphrag", "deep_graphrag"}
SAMPLE_FILES = {
    "hotpotqa": SAMPLE_ROOT / "hotpotqa_sample.jsonl",
    "twowiki": SAMPLE_ROOT / "twowiki_sample.jsonl",
    "2wikimultihopqa": SAMPLE_ROOT / "twowiki_sample.jsonl",
    "musique": SAMPLE_ROOT / "musique_sample.jsonl",
}


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[\w\u4e00-\u9fff]+", str(text or "").lower()))


def resolve_input_path(*, dataset: str, split: str, input_path: Path | None) -> Path:
    if input_path is not None:
        return Path(input_path)
    normalized = dataset.strip().lower()
    if normalized not in SAMPLE_FILES:
        raise ValueError(f"Unsupported dataset: {dataset}")
    return SAMPLE_FILES[normalized]


def _dataset_label(dataset: str) -> str:
    normalized = dataset.strip().lower()
    if normalized in {"twowiki", "2wikimultihopqa"}:
        return "twowiki"
    return normalized


def _doc_score(question: str, document: dict[str, Any], *, mode: str) -> float:
    question_tokens = _tokenize(question)
    title_tokens = _tokenize(document.get("title") or "")
    text_tokens = _tokenize(document.get("text") or "")
    overlap = len(question_tokens & text_tokens)
    title_overlap = len(question_tokens & title_tokens)
    score = float(overlap * 2 + title_overlap * 3)
    if mode in {"local_graphrag", "deep_graphrag"}:
        score += float(len(title_tokens) * 0.05)
    if mode == "deep_graphrag":
        score += 1.0 if len(document.get("sentences") or []) > 1 else 0.25
    return score


def _rank_documents(record: dict[str, Any], *, mode: str) -> list[dict[str, Any]]:
    ranked = sorted(
        record.get("documents") or [],
        key=lambda document: (
            _doc_score(record.get("question") or "", document, mode=mode),
            len(document.get("text") or ""),
        ),
        reverse=True,
    )
    return ranked


def _doc_recall(retrieved: list[dict[str, Any]], support: list[dict[str, Any]], k: int) -> float:
    if not support:
        return 0.0
    support_titles = {item["title"] for item in support}
    retrieved_titles = {item["title"] for item in retrieved[:k]}
    return len(support_titles & retrieved_titles) / len(support_titles)


def _supporting_evidence_recall(retrieved: list[dict[str, Any]], support: list[dict[str, Any]]) -> float:
    if not support:
        return 0.0
    matched = 0
    for evidence in support:
        for document in retrieved:
            if document.get("title") == evidence.get("title") and evidence.get("text") in (document.get("text") or ""):
                matched += 1
                break
    return matched / len(support)


def _evidence_chain_recall(retrieved: list[dict[str, Any]], record: dict[str, Any]) -> float | None:
    evidence_path = list(record.get("gold_evidence_path") or [])
    if not evidence_path:
        return None
    titles = {document.get("title") for document in retrieved}
    covered = 0
    for edge in evidence_path:
        subject = edge.get("subject")
        object_ = edge.get("object")
        if subject in titles or object_ in titles:
            covered += 1
    return covered / len(evidence_path)


def _answer_scores(retrieved: list[dict[str, Any]], answer: str) -> tuple[float | None, float | None]:
    if not answer:
        return None, None
    normalized_answer = str(answer).strip().lower()
    if not normalized_answer:
        return None, None
    found = any(normalized_answer in str(document.get("text") or "").lower() for document in retrieved)
    return (1.0 if found else 0.0, 1.0 if found else 0.0)


def _route_metadata(mode: str) -> dict[str, Any]:
    if mode == "baseline_rag":
        return {
            "requested_mode": "baseline_rag",
            "resolved_mode": "baseline_rag",
            "internal_route": "mocked_standard_rag",
            "used_vector": True,
            "used_bm25": False,
            "used_graph": False,
            "used_communities": [],
            "follow_up_questions": [],
            "stackless_or_mocked": "mocked",
        }
    if mode == "local_graphrag":
        return {
            "requested_mode": "local_graphrag",
            "resolved_mode": "local_graphrag",
            "internal_route": "mocked_local_graphrag",
            "used_vector": True,
            "used_bm25": False,
            "used_graph": True,
            "used_communities": [],
            "follow_up_questions": [],
            "stackless_or_mocked": "mocked",
        }
    return {
        "requested_mode": "deep_graphrag",
        "resolved_mode": "deep_graphrag",
        "internal_route": "mocked_drift_like",
        "used_vector": True,
        "used_bm25": False,
        "used_graph": True,
        "used_communities": ["mocked-community-0"],
        "follow_up_questions": ["mocked follow-up"],
        "stackless_or_mocked": "mocked",
    }


def _aggregate_metrics(rows: list[dict[str, Any]]) -> dict[str, float | None]:
    metric_names = [
        "Recall@2",
        "Recall@5",
        "Recall@10",
        "Supporting Evidence Recall",
        "Evidence Chain Recall",
        "Answer EM",
        "Answer F1",
    ]
    aggregate: dict[str, float | None] = {}
    for name in metric_names:
        values = [row["metrics"][name] for row in rows if row["metrics"][name] is not None]
        aggregate[name] = (sum(values) / len(values)) if values else None
    return aggregate


def _build_compare_matrix(*, dataset: str, output_root: Path) -> dict[str, Any]:
    normalized = _dataset_label(dataset)
    reports = {}
    for mode in sorted(SUPPORTED_MODES):
        report_path = output_root / f"{normalized}_{mode}.json"
        if report_path.exists():
            reports[mode] = json.loads(report_path.read_text(encoding="utf-8"))
    matrix = {
        "dataset": normalized,
        "execution_mode": "mocked",
        "modes": sorted(reports.keys()),
        "reports": {
            mode: {
                "metrics": payload.get("metrics", {}),
                "sample_count": payload.get("sample_count", 0),
                "report_path": str(output_root / f"{normalized}_{mode}.json"),
            }
            for mode, payload in reports.items()
        },
    }
    _write_json(output_root / "compare_matrix.json", matrix)
    return matrix


def run_multihop_eval(
    *,
    dataset: str,
    mode: str,
    split: str,
    limit: int,
    input_path: Path | None,
    output_root: Path,
) -> dict[str, Any]:
    if mode not in SUPPORTED_MODES:
        raise ValueError(f"Unsupported mode: {mode}")

    resolved_input = resolve_input_path(dataset=dataset, split=split, input_path=input_path)
    records = _read_jsonl(resolved_input)[: max(limit, 0)]
    result_rows: list[dict[str, Any]] = []

    for record in records:
        ranked = _rank_documents(record, mode=mode)
        metrics = {
            "Recall@2": _doc_recall(ranked, record.get("gold_support") or [], 2),
            "Recall@5": _doc_recall(ranked, record.get("gold_support") or [], 5),
            "Recall@10": _doc_recall(ranked, record.get("gold_support") or [], 10),
            "Supporting Evidence Recall": _supporting_evidence_recall(ranked[:10], record.get("gold_support") or []),
            "Evidence Chain Recall": _evidence_chain_recall(ranked[:10], record),
        }
        answer_em, answer_f1 = _answer_scores(ranked[:10], str(record.get("answer") or ""))
        metrics["Answer EM"] = answer_em
        metrics["Answer F1"] = answer_f1
        result_rows.append(
            {
                "id": record.get("id"),
                "question": record.get("question"),
                "metrics": metrics,
                "retrieved_titles": [document.get("title") for document in ranked[:10]],
                "route_metadata": _route_metadata(mode),
            }
        )

    normalized_dataset = _dataset_label(dataset)
    report = {
        "dataset": normalized_dataset,
        "mode": mode,
        "split": split,
        "execution_mode": "mocked",
        "input_path": str(resolved_input),
        "sample_count": len(result_rows),
        "metrics": _aggregate_metrics(result_rows),
        "results": result_rows,
        "notes": [
            "This is a mocked smoke runner.",
            "It does not claim real GraphRAG quality.",
            "Use it only to validate adapter and reporting shape before real runtime eval.",
        ],
    }
    report_path = output_root / f"{normalized_dataset}_{mode}.json"
    _write_json(report_path, report)
    compare_matrix = _build_compare_matrix(dataset=dataset, output_root=output_root)
    return {
        "dataset": normalized_dataset,
        "mode": mode,
        "execution_mode": "mocked",
        "report_path": str(report_path),
        "compare_matrix_path": str(output_root / "compare_matrix.json"),
        "metrics": report["metrics"],
        "modes_in_matrix": compare_matrix["modes"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run mocked multi-hop smoke evaluation.")
    parser.add_argument("--dataset", required=True, choices=["hotpotqa", "twowiki", "musique"])
    parser.add_argument("--mode", required=True, choices=sorted(SUPPORTED_MODES))
    parser.add_argument("--split", default="dev")
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_ROOT)
    args = parser.parse_args()

    result = run_multihop_eval(
        dataset=args.dataset,
        mode=args.mode,
        split=args.split,
        limit=args.limit,
        input_path=args.input,
        output_root=args.output,
    )
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()

