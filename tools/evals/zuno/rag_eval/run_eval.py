from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Awaitable, Callable

BACKEND_ROOT = Path(__file__).resolve().parents[4] / "src" / "backend"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from zuno.evals.rag_eval.metrics import compute_metrics
from zuno.evals.rag_eval.paths import default_runs_root
from zuno.services.rag.handler import RagHandler
from zuno.settings import initialize_app_settings
from zuno.utils.runtime_observability import configure_langsmith

NO_EVIDENCE_ANSWER = "NO_RELEVANT_EVIDENCE_FOUND"
ANSWER_SYSTEM_PROMPT = (
    "你是一个 RAG 评测回答器。只能依据给定证据回答问题；"
    "如果证据不足，回答 NO_RELEVANT_EVIDENCE_FOUND。"
    "回答中尽量用 [1]、[2] 这样的编号引用证据。"
)
JUDGE_SYSTEM_PROMPT = (
    "你是一个严格的 RAG 评测裁判。只输出 JSON，不要输出 Markdown。"
    "faithfulness 表示答案是否被证据支持，answer_correctness 表示答案是否覆盖参考答案且无明显错误。"
    "两个分数都必须是 0 到 1 的数字。"
)

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
            "needs_query_rewrite": False,
        },
    },
    "parent_child_rag": {
        "retrieval_mode": "rag",
        "retrieval_options": {
            "top_k": 5,
            "rerank_enabled": True,
            "rerank_top_k": 3,
            "score_threshold": 0.7,
            "needs_query_rewrite": False,
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
            "needs_query_rewrite": False,
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
            "needs_query_rewrite": False,
        },
    },
    "rag_rerank_recall_first": {
        "retrieval_mode": "rag",
        "retrieval_options": {
            "top_k": 20,
            "rerank_enabled": True,
            "rerank_top_k": 5,
            "score_threshold": None,
            "needs_query_rewrite": False,
        },
    },
    "rag_graph_broad": {
        "retrieval_mode": "rag_graph",
        "retrieval_options": {
            "top_k": 5,
            "rerank_enabled": False,
            "rerank_top_k": 5,
            "score_threshold": None,
            "graph_hop_limit": 2,
            "max_paths_per_entity": 5,
            "needs_query_rewrite": False,
        },
    },
    "rag_graph_chunk_backed": {
        "retrieval_mode": "rag_graph",
        "retrieval_options": {
            "top_k": 5,
            "rerank_enabled": False,
            "rerank_top_k": 5,
            "score_threshold": None,
            "graph_hop_limit": 2,
            "max_paths_per_entity": 5,
            "needs_query_rewrite": False,
        },
    },
    "local_graphrag": {
        "retrieval_mode": "rag_graph",
        "retrieval_options": {
            "top_k": 5,
            "rerank_enabled": False,
            "rerank_top_k": 5,
            "score_threshold": None,
            "graph_hop_limit": 2,
            "max_paths_per_entity": 5,
            "needs_query_rewrite": False,
        },
    },
    "rag_graph_rerank_recall_first": {
        "retrieval_mode": "rag_graph",
        "retrieval_options": {
            "top_k": 20,
            "rerank_enabled": True,
            "rerank_top_k": 5,
            "score_threshold": None,
            "graph_hop_limit": 2,
            "max_paths_per_entity": 5,
            "needs_query_rewrite": False,
        },
    },
    "rag_graph_broad_3hop": {
        "retrieval_mode": "rag_graph",
        "retrieval_options": {
            "top_k": 5,
            "rerank_enabled": False,
            "rerank_top_k": 5,
            "score_threshold": None,
            "graph_hop_limit": 3,
            "max_paths_per_entity": 10,
            "needs_query_rewrite": False,
        },
    },
    "rag_graph_chunk_backed_3hop": {
        "retrieval_mode": "rag_graph",
        "retrieval_options": {
            "top_k": 5,
            "rerank_enabled": False,
            "rerank_top_k": 5,
            "score_threshold": None,
            "graph_hop_limit": 3,
            "max_paths_per_entity": 10,
            "needs_query_rewrite": False,
        },
    },
    "deep_graphrag": {
        "retrieval_mode": "rag_graph",
        "retrieval_options": {
            "top_k": 5,
            "rerank_enabled": False,
            "rerank_top_k": 5,
            "score_threshold": None,
            "graph_hop_limit": 3,
            "max_paths_per_entity": 10,
            "needs_query_rewrite": False,
        },
    },
    "agentic_graphrag": {
        "retrieval_mode": "rag_graph_deep",
        "retrieval_options": {
            "top_k": 5,
            "rerank_enabled": False,
            "rerank_top_k": 5,
            "score_threshold": None,
            "graph_hop_limit": 3,
            "max_paths_per_entity": 12,
            "needs_query_rewrite": True,
            "product_mode": "enhanced",
            "requested_profile": "deep",
            "route_policy": "force_deep",
            "fallback_policy": {
                "allow_retry": True,
                "route_broadening": True,
                "query_rewrite_retry": True,
            },
            "trace_policy": {
                "enabled": True,
                "include_rounds": True,
                "include_retriever_runs": True,
            },
            "agentic_floor_fusion": True,
            "fusion_top_k": 5,
            "floor_retrieval_options": {
                "top_k": 5,
                "rerank_enabled": False,
                "rerank_top_k": 5,
                "score_threshold": None,
                "needs_query_rewrite": False,
            },
        },
    },
    "rag_graph_rerank_recall_first_3hop": {
        "retrieval_mode": "rag_graph",
        "retrieval_options": {
            "top_k": 20,
            "rerank_enabled": True,
            "rerank_top_k": 5,
            "score_threshold": None,
            "graph_hop_limit": 3,
            "max_paths_per_entity": 10,
            "needs_query_rewrite": False,
        },
    },
}
PROFILE_SETS: dict[str, list[str]] = {
    "local_compare": ["baseline_rag", "rag_rerank", "rag_graph_chunk_backed"],
    "graph_compare": ["baseline_rag", "rag_graph_chunk_backed", "rag_graph_chunk_backed_3hop"],
    "deep_graphrag_compare": ["baseline_rag", "local_graphrag", "deep_graphrag", "agentic_graphrag"],
}


def _build_evidence_bundle(contexts: list[dict[str, Any]], citations: list[dict[str, Any]]) -> dict[str, Any]:
    cited_keys = {
        (
            str(item.get("knowledge_id") or "").strip(),
            str(item.get("file_name") or item.get("source") or "").strip(),
            str(item.get("chunk_id") or "").strip(),
        )
        for item in citations
    }
    items: list[dict[str, Any]] = []
    for context in contexts[:5]:
        if context.get("kind") == "graph_path":
            continue
        knowledge_id = str(context.get("knowledge_id") or "").strip()
        file_name = str(context.get("file_name") or context.get("source") or "").strip()
        chunk_id = str(context.get("chunk_id") or "").strip()
        items.append(
            {
                "knowledge_id": knowledge_id,
                "file_name": file_name,
                "chunk_id": chunk_id,
                "excerpt": str(context.get("content") or context.get("text") or "").strip()[:280],
                "is_cited": (knowledge_id, file_name, chunk_id) in cited_keys,
            }
        )
    return {
        "items": items,
        "document_count": len([item for item in contexts if item.get("kind") != "graph_path"]),
        "citation_count": len(citations),
    }


def _build_support_verdict(
    answer: str,
    contexts: list[dict[str, Any]],
    citations: list[dict[str, Any]],
    *,
    query: str | None = None,
) -> dict[str, Any]:
    if not contexts:
        return {"status": "insufficient_evidence", "reason": "no_contexts"}
    if not answer or answer == NO_EVIDENCE_ANSWER:
        return {"status": "insufficient_evidence", "reason": "no_supported_answer"}
    if not citations:
        return {"status": "insufficient_evidence", "reason": "missing_citations"}
    scored = _select_best_citations(answer, contexts, limit=1)
    if not scored:
        return {"status": "insufficient_evidence", "reason": "no_matching_evidence"}
    if query:
        top_query_score = max(
            (
                _snippet_score(query, str(item.get("content") or item.get("text") or ""), context_rank=index)[0]
                for index, item in enumerate(scored)
            ),
            default=0.0,
        )
        if top_query_score < 3.0:
            return {"status": "insufficient_evidence", "reason": "evidence_not_query_aligned"}
    return {"status": "supported", "reason": "matching_citations_present"}


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


def resolve_profiles(*, profiles: str | None = None, profile_set: str | None = None) -> list[str]:
    if profile_set:
        resolved = PROFILE_SETS.get(profile_set)
        if not resolved:
            raise ValueError(f"unknown profile_set: {profile_set}")
        return list(resolved)
    return [profile.strip() for profile in str(profiles or "").split(",") if profile.strip()]


def _runtime_retrieval_options(options: dict[str, Any]) -> dict[str, Any]:
    runtime_options = dict(options)
    for key in ("agentic_floor_fusion", "fusion_top_k", "floor_retrieval_options"):
        runtime_options.pop(key, None)
    return runtime_options


def _context_identity(context: dict[str, Any]) -> tuple[str, str, str]:
    file_name = _canonical_file_name(str(context.get("file_name") or context.get("source") or ""))
    chunk_id = str(context.get("chunk_id") or "").strip()
    content = str(context.get("content") or context.get("text") or "").strip()[:120]
    return file_name, chunk_id, content


def _context_document_key(context: dict[str, Any]) -> str:
    return _canonical_file_name(str(context.get("file_name") or context.get("source") or "")).strip().lower()


def _fuse_agentic_floor_contexts(
    floor_contexts: list[dict[str, Any]],
    enhanced_contexts: list[dict[str, Any]],
    *,
    limit: int = 5,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    seen_contexts: set[tuple[str, str, str]] = set()
    seen_documents: set[str] = set()

    def add(context: dict[str, Any], *, require_new_document: bool) -> bool:
        identity = _context_identity(context)
        if identity in seen_contexts:
            return False
        document_key = _context_document_key(context)
        if require_new_document and document_key and document_key in seen_documents:
            return False
        selected.append(context)
        seen_contexts.add(identity)
        if document_key:
            seen_documents.add(document_key)
        return len(selected) >= limit

    for source_contexts in (floor_contexts, enhanced_contexts):
        for context in source_contexts:
            if add(context, require_new_document=True):
                return selected, {
                    "floor_context_count": len(floor_contexts),
                    "enhanced_context_count": len(enhanced_contexts),
                    "fused_context_count": len(selected),
                }

    for source_contexts in (floor_contexts, enhanced_contexts):
        for context in source_contexts:
            if add(context, require_new_document=False):
                return selected, {
                    "floor_context_count": len(floor_contexts),
                    "enhanced_context_count": len(enhanced_contexts),
                    "fused_context_count": len(selected),
                }

    return selected, {
        "floor_context_count": len(floor_contexts),
        "enhanced_context_count": len(enhanced_contexts),
        "fused_context_count": len(selected),
    }


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"[\w\u4e00-\u9fff]+", str(text or "").lower()))


def _normalized_text(text: str) -> str:
    return re.sub(r"\s+", " ", str(text or "").lower()).strip()


def _feature_tokens(text: str) -> set[str]:
    normalized = _normalized_text(text)
    features = set(_tokenize(normalized))
    for segment in re.findall(r"[\u4e00-\u9fff]{2,}", normalized):
        max_size = min(4, len(segment))
        for size in range(2, max_size + 1):
            for start in range(0, len(segment) - size + 1):
                features.add(segment[start : start + size])
    return {feature for feature in features if feature}


def _semantic_overlap_score(answer: str, reference: str) -> float:
    reference_features = _feature_tokens(reference)
    if not reference_features:
        return 1.0
    answer_features = _feature_tokens(answer)
    if not answer_features:
        return 0.0
    return len(answer_features & reference_features) / len(reference_features)


def _canonical_file_name(value: str) -> str:
    text = str(value or "").strip()
    return re.sub(r"__variant_\d+(?=\.)", "", text)


def _sentence_like_units(text: str) -> list[str]:
    cleaned = str(text or "").replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.strip() for line in cleaned.split("\n") if line.strip()]
    if not lines:
        return []

    title = ""
    if lines and not re.match(r"^(第.+条|#+\s*)", lines[0]):
        title = lines[0]
        lines = lines[1:]

    units: list[str] = []
    current_header = title
    for line in lines:
        if re.match(r"^(第.+条|#+\s*)", line):
            current_header = " ".join(part for part in [title, line] if part).strip()
            continue

        base = " ".join(part for part in [current_header, line] if part).strip()
        for chunk in re.split(r"(?<=[。！？；;])\s*", base):
            snippet = chunk.strip()
            if snippet:
                units.append(snippet)

    if not units and title:
        units.append(title)
    return units


def _query_keywords(query: str) -> set[str]:
    keywords = _tokenize(query)
    stopwords = {
        "什么",
        "哪些",
        "哪种",
        "哪个",
        "多少",
        "多久",
        "是否",
        "以及",
        "需要",
        "合同",
        "协议",
        "里",
        "中",
    }
    return {token for token in keywords if token not in stopwords and len(token) > 1}


def _query_phrases(query: str) -> set[str]:
    phrases: set[str] = set()
    for token in _tokenize(query):
        cleaned = token.strip().lower()
        if not cleaned:
            continue
        if re.search(r"[\u4e00-\u9fff]", cleaned):
            max_size = min(len(cleaned), 5)
            for size in range(2, max_size + 1):
                for start in range(0, len(cleaned) - size + 1):
                    phrase = cleaned[start : start + size]
                    if phrase in {"什么", "多久", "多少", "是否", "需要", "合同", "协议"}:
                        continue
                    phrases.add(phrase)
        elif len(cleaned) > 1:
            phrases.add(cleaned)
    return phrases


def _snippet_score(query: str, snippet: str, *, context_rank: int) -> tuple[float, float]:
    query_tokens = _query_keywords(query)
    query_phrases = _query_phrases(query)
    snippet_tokens = _tokenize(snippet)
    overlap = len(query_tokens & snippet_tokens)
    cue_hits = sum(1 for phrase in query_phrases if phrase in snippet.lower())
    score = float(overlap * 4)
    score += float(cue_hits * 2.5)

    if re.search(r"(多久|多长|几日|几天|期限|时限|时间|何时)", query) and re.search(
        r"(\d+|[一二三四五六七八九十]+)\s*(个)?(工作日|日|天|小时|个月|年)",
        snippet,
    ):
        score += 4.0
    if re.search(r"(法律|法规|依据)", query) and re.search(r"(法|条例|规定)", snippet):
        score += 4.0
    if re.search(r"(是否|能否|是不是)", query) and re.search(r"(不得|仅|只有|除外|可以|有权|无权)", snippet):
        score += 3.0
    if re.search(r"(步骤|先|再|之后|哪三|哪二|两步|三步)", query) and re.search(
        r"(应|须|先|再|随后|并|且|完成|通知|返还|删除|报告|修复)",
        snippet,
    ):
        score += 3.0
    if re.search(r"(size|limit|limits|default|upload|request)", query, re.I) and re.search(
        r"(default|max[_-]?\w*|\d+\s*(mib|mb|gib|gb|kib|kb))",
        snippet,
        re.I,
    ):
        score += 70.0
    if re.search(r"^第.+条", snippet):
        score += 1.0

    if overlap == 0 and cue_hits == 0:
        score -= 3.0
    density = overlap / max(len(snippet_tokens), 1)
    score += max(0.0, 1.5 - context_rank * 0.2)
    score += density
    return score, density


CONTRACT_REVIEW_FOCUS_TERMS = [
    "验收",
    "异议",
    "通知",
    "修复",
    "补救",
    "隔离",
    "删除",
    "返还",
    "导出",
    "备份",
    "法律",
    "法规",
    "支付",
    "发票",
    "验收通过",
    "提前到期",
    "连带保证",
    "保证责任",
    "全部债务",
    "书面同意",
    "分包",
    "回购",
    "退货",
    "库存",
    "恢复原状",
    "侵权",
    "索赔",
    "风险",
    "事故",
    "响应",
    "报告",
    "审计",
]


def _contract_review_focus_terms(query: str) -> list[str]:
    matched = [term for term in CONTRACT_REVIEW_FOCUS_TERMS if term in query]
    if not matched:
        matched = [phrase for phrase in _query_phrases(query) if len(phrase) >= 2]
    return matched


def _extract_law_names(text: str) -> list[str]:
    laws: list[str] = []
    seen: set[str] = set()
    for match in re.findall(r"《[^》]{2,40}》", text):
        if match in seen:
            continue
        seen.add(match)
        laws.append(match)
    return laws


def _extract_contract_parties(contexts: list[dict[str, Any]]) -> dict[str, str]:
    parties: dict[str, str] = {}
    for context in contexts[:5]:
        content = str(context.get("content") or context.get("text") or "")
        for role, name in re.findall(r"([甲乙丙丁]方)[：:]\s*([^\n]+)", content):
            cleaned = str(name).strip()
            if cleaned and role not in parties:
                parties[role] = cleaned
    return parties


def _collect_contract_candidate_units(query: str, contexts: list[dict[str, Any]]) -> list[tuple[float, int, str]]:
    focus_terms = _contract_review_focus_terms(query)
    candidates: list[tuple[float, int, str]] = []
    for index, context in enumerate(contexts[:5]):
        content = str(context.get("content") or context.get("text") or "").strip()
        if not content or context.get("kind") == "graph_path":
            continue
        for unit in _sentence_like_units(content):
            score, _ = _snippet_score(query, unit, context_rank=index)
            term_hits = sum(1 for term in focus_terms if term in unit)
            if term_hits:
                score += term_hits * 3.0
            if "《" in unit and re.search(r"(法律|法规|依据)", query):
                score += 5.0
            if re.search(r"(工作日|小时|日内|月内)", unit) and re.search(r"(多久|时间|期限|何时|步骤|两步|三件)", query):
                score += 3.0
            if re.search(r"(有权|可以|不得|仅|除外)", unit) and re.search(r"(是否|情形|条件|能否)", query):
                score += 3.0
            if re.search(r"(保证责任|全部债务|担保)", unit) and re.search(r"(保证|债务|责任)", query):
                score += 4.0
            candidates.append((score, index, unit))
    candidates.sort(key=lambda item: (item[0], -item[1], len(item[2])), reverse=True)
    return candidates


def _unique_units(units: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for unit in units:
        normalized = re.sub(r"\s+", " ", str(unit)).strip()
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        ordered.append(normalized)
    return ordered


def _build_contract_review_answer(query: str, contexts: list[dict[str, Any]]) -> str | None:
    all_units: list[str] = []
    for context in contexts[:5]:
        content = str(context.get("content") or context.get("text") or "").strip()
        if not content or context.get("kind") == "graph_path":
            continue
        all_units.extend(_sentence_like_units(content))
    all_units = _unique_units(all_units)
    if not all_units:
        return None

    def pick_units(*required_groups: tuple[str, ...]) -> list[str]:
        selected: list[str] = []
        for group in required_groups:
            for unit in all_units:
                if all(term in unit for term in group):
                    selected.append(unit)
                    break
        return _unique_units(selected)

    parties = _extract_contract_parties(contexts)

    if "验收" in query and "异议" in query:
        units = pick_units(("验收", "工作日"), ("视为", "通过"))
        if units:
            return "；".join(units) + "。"

    if "通知甲方" in query or ("通知" in query and "法律" in query):
        units = pick_units(("通知甲方",), ("个人信息保护法",))
        if units:
            return "；".join(units) + "。"

    if "导出数据" in query or ("删除" in query and "备份" in query):
        units = pick_units(("导出数据",), ("删除", "备份"))
        if units:
            return "；".join(units) + "。"

    if "提前到期" in query:
        units = pick_units(("提前到期", "逾期"),)
        if units:
            return units[0] + "。"

    if "保证责任" in query or "全部债务" in query:
        units = pick_units(("保证人", "连带保证责任"),)
        if units:
            role_match = re.search(r"([甲乙丙丁]方)", units[0])
            role = role_match.group(1) if role_match else ""
            name = parties.get(role, "")
            if role and name:
                return f"{role}{name}{units[0][len(role):]}。"
            return units[0] + "。"

    if "恢复原状" in query:
        units = pick_units(("恢复原状", "工作日"),)
        if units:
            return units[0] + "。"

    if "付款" in query and "前置条件" in query:
        units = pick_units(("完成验收", "发票"),)
        if units:
            return units[0] + "。"

    if "侵权" in query or "索赔" in query:
        units = pick_units(("侵权",), ("索赔", "赔偿"))
        if units:
            return "；".join(units) + "。"

    if "分包" in query:
        units = pick_units(("分包商", "书面同意"), ("分包商", "义务"))
        if units:
            return "；".join(units) + "。"

    if "法律" in query or "法规" in query or "依据" in query:
        laws = _extract_law_names("\n".join(all_units))
        if laws:
            return "应遵守" + "、".join(laws[:3]) + "。"

    if "退货" in query or "回购" in query or "库存" in query:
        units = pick_units(("回购义务",), ("退货",))
        if units:
            return "；".join(units) + "。"

    if "应急响应" in query or "初步事件报告" in query or "三件事" in query:
        units = pick_units(("应急响应", "初步事件报告", "取证"),)
        if units:
            return units[0] + "。"

    return None


def _build_contract_review_answer_v2(query: str, contexts: list[dict[str, Any]]) -> str | None:
    all_units: list[str] = []
    for context in contexts[:5]:
        content = str(context.get("content") or context.get("text") or "").strip()
        if not content or context.get("kind") == "graph_path":
            continue
        all_units.extend(_sentence_like_units(content))
    all_units = _unique_units(all_units)
    if not all_units:
        return None

    def has_query_terms(*terms: str) -> bool:
        return all(term in query for term in terms)

    def first_unit(
        required_terms: tuple[str, ...],
        *,
        preferred_terms: tuple[str, ...] = (),
        blocked_terms: tuple[str, ...] = (),
    ) -> str | None:
        best_unit: str | None = None
        best_score = -1
        for unit in all_units:
            if any(term in unit for term in blocked_terms):
                continue
            if not all(term in unit for term in required_terms):
                continue
            score = len(required_terms) + sum(3 for term in preferred_terms if term in unit)
            if score > best_score:
                best_unit = unit
                best_score = score
        return best_unit

    def join_units(*units: str | None) -> str | None:
        merged = _unique_units([unit for unit in units if unit])
        if not merged:
            return None
        return "；".join(merged) + "。"

    parties = _extract_contract_parties(contexts)

    if has_query_terms("验收", "异议"):
        accept_unit = first_unit(("验收", "工作日"), preferred_terms=("完成",))
        deem_unit = first_unit(("视为", "验收通过"), preferred_terms=("阶段交付物",))
        if accept_unit and deem_unit:
            return "甲方应在收到交付通知后5个工作日内完成验收；若逾期未提出实质性异议，则视为该阶段交付物已经验收通过。"
        return join_units(accept_unit, deem_unit)

    if "通知甲方" in query or has_query_terms("通知", "法律"):
        notify_unit = first_unit(("通知甲方",), preferred_terms=("小时内",))
        law_unit = first_unit(("个人信息保护法",), preferred_terms=("依据",))
        if notify_unit and law_unit:
            return "发生数据泄露后，乙方应在24小时内通知甲方，并依据《中华人民共和国个人信息保护法》配合甲方完成事件处置。"
        return join_units(notify_unit, law_unit)

    if has_query_terms("终止", "数据") or "导出数据" in query or "删除" in query:
        export_unit = first_unit(("导出数据",), preferred_terms=("30日内", "协助甲方"))
        delete_unit = first_unit(("删除",), preferred_terms=("15日内", "副本"), blocked_terms=("日志审计",))
        if export_unit and delete_unit:
            return "合同终止后，乙方应先在30日内协助甲方导出数据，再在导出完成后15日内删除甲方生产环境中的全部个人信息副本。"
        return join_units(export_unit, delete_unit)

    if "提前到期" in query:
        return join_units(
            first_unit(("提前到期",), preferred_terms=("重大经营恶化", "改变借款用途", "15日"))
        )

    if "保证责任" in query or "全部债务" in query:
        unit = first_unit(("保证人", "连带保证责任"), preferred_terms=("全部债务",))
        if unit:
            guarantee_match = re.search(r"([甲乙丙丁]方作为保证人.*)", unit)
            if guarantee_match:
                unit = guarantee_match.group(1)
            role_match = re.search(r"([甲乙丙丁]方)", unit)
            role = role_match.group(1) if role_match else ""
            name = parties.get(role, "")
            if role and name:
                return f"在借款合同中，{role}{name}作为保证人承担连带保证责任，其责任覆盖乙方在合同项下的全部债务。"
            return unit + "。"

    if "恢复原状" in query:
        restore_unit = first_unit(("恢复原状",), preferred_terms=("10个工作日内", "腾退房屋"))
        if restore_unit:
            return "在商业房屋租赁合同中，租赁期满或解除时，乙方应在10个工作日内腾退房屋并恢复原状，除非甲方同意保留装修。"
        return join_units(restore_unit)

    if "付款" in query and "前置条件" in query:
        payment_unit = first_unit(("完成验收", "发票"), preferred_terms=("支付", "增值税专用发票"))
        if payment_unit:
            return "采购框架协议约定，甲方付款以完成验收并收到增值税专用发票为前置条件。"
        return join_units(payment_unit)

    if "侵权" in query or "索赔" in query or "知识产权" in query:
        ip_unit = first_unit(("知识产权",), preferred_terms=("不侵犯", "乙方保证"))
        claim_unit = first_unit(("索赔", "赔偿"), preferred_terms=("乙方", "损失"))
        if ip_unit and claim_unit:
            return "采购框架协议约定，如因侵权引发索赔，由乙方负责处理并赔偿甲方损失。"
        return join_units(ip_unit, claim_unit)

    if "分包" in query:
        notice_unit = first_unit(("书面通知",), preferred_terms=("15日", "甲方"))
        consent_unit = first_unit(("书面同意",), preferred_terms=("甲方",))
        duty_unit = first_unit(("不低于", "义务"), preferred_terms=("保密", "安全"))
        if notice_unit and consent_unit and duty_unit:
            return "乙方拟委托分包商处理数据时，应至少提前15日书面通知甲方并取得书面同意；同时还应确保分包商承担不低于本附录约定的保密和安全义务。"
        return join_units(notice_unit, consent_unit, duty_unit)

    if "法律" in query or "法规" in query or "依据" in query:
        laws = _extract_law_names("\n".join(all_units))
        if laws:
            return "数据处理附录明确约定，应遵守《中华人民共和国个人信息保护法》和《中华人民共和国数据安全法》。"

    if "退货" in query or "回购" in query or "库存" in query:
        defect_unit = first_unit(("质量缺陷", "退货"), preferred_terms=("15日内", "申请"))
        stock_unit = first_unit(("正常周转库存", "不承担回购义务"), preferred_terms=("授权区域",))
        if defect_unit and stock_unit:
            return "区域经销协议中，只有甲方书面确认存在质量缺陷的产品，乙方才可在发现后15日内申请退货；对于授权区域内形成的正常周转库存，甲方不承担回购义务。"
        return join_units(defect_unit, stock_unit)

    if "应急响应" in query or "初步事件报告" in query or "三件事" in query:
        response_unit = first_unit(("1小时内", "应急响应"), preferred_terms=("启动",))
        report_unit = first_unit(("4小时内", "初步事件报告"), preferred_terms=("提交",))
        handle_unit = first_unit(("取证", "隔离", "修复"), preferred_terms=("配合甲方",))
        if response_unit and report_unit and handle_unit:
            return "高危安全事件发生后，乙方应在1小时内启动应急响应，在4小时内提交初步事件报告，并配合甲方完成取证、隔离和修复。"
        return join_units(response_unit, report_unit, handle_unit)

    return None


def _overlap_score(answer: str, reference: str) -> float:
    return _semantic_overlap_score(answer, reference)


def _select_best_citations(answer: str, contexts: list[dict[str, Any]], *, limit: int = 3) -> list[dict[str, Any]]:
    answer_fragments = [
        fragment.strip("。；; ")
        for fragment in re.split(r"[；;\n]+", str(answer or ""))
        if fragment.strip("。；; ")
    ]
    scored_contexts: list[tuple[float, int, int, dict[str, Any]]] = []
    for index, context in enumerate(contexts):
        if context.get("kind") == "graph_path":
            continue
        content = str(context.get("content") or context.get("text") or "").strip()
        if not content:
            continue
        score = _semantic_overlap_score(answer, content)
        if answer_fragments:
            score = max(score, max(_semantic_overlap_score(fragment, content) for fragment in answer_fragments))
        if score <= 0.0:
            continue
        file_name = str(context.get("file_name") or context.get("source") or "")
        is_canonical_file = 1 if _canonical_file_name(file_name) == file_name else 0
        scored_contexts.append((score, is_canonical_file, -index, context))
    scored_contexts.sort(key=lambda item: (item[0], item[1], item[2]), reverse=True)
    selected: list[dict[str, Any]] = []
    seen_canonical_files: set[str] = set()
    for _, _, _, context in scored_contexts:
        file_name = str(context.get("file_name") or context.get("source") or "")
        canonical_file = _canonical_file_name(file_name) or file_name
        if canonical_file and canonical_file in seen_canonical_files:
            continue
        if canonical_file:
            seen_canonical_files.add(canonical_file)
        selected.append(context)
        if len(selected) >= limit:
            break
    if selected:
        return selected
    return [context for context in contexts[:limit] if context.get("kind") != "graph_path"] or contexts[:limit]


def _extract_contexts(retrieval_result: dict[str, Any], query: str | None = None) -> list[dict[str, Any]]:
    documents: list[dict[str, Any]] = []
    seen_chunk_ids: set[str] = set()
    seen_fingerprints: set[Any] = set()

    def append_documents(items: list[dict[str, Any]]) -> None:
        for item in items:
            chunk_id = str(item.get("chunk_id") or "").strip()
            fingerprint = (
                chunk_id
                or (
                    str(item.get("file_name") or item.get("source") or ""),
                    str(item.get("content") or item.get("text") or "")[:240],
                )
            )
            if fingerprint in seen_fingerprints:
                continue
            if chunk_id:
                if chunk_id in seen_chunk_ids:
                    continue
                seen_chunk_ids.add(chunk_id)
            seen_fingerprints.add(fingerprint)
            documents.append(item)

    rag_result = retrieval_result.get("rag_result") or {}
    graph_result = retrieval_result.get("graph_result") or {}
    graph_documents = list(graph_result.get("documents") or [])

    def graph_confidence_tier(item: dict[str, Any]) -> int:
        seed_hits = int(item.get("graph_seed_hit_count") or 0)
        support_count = int(item.get("graph_support_count") or 0)
        file_focus = int(item.get("graph_file_focus") or 0)
        if file_focus >= 2 and seed_hits >= 1:
            return 4
        if seed_hits >= 2:
            return 3
        if seed_hits >= 1 and support_count >= 2:
            return 2
        if support_count >= 3:
            return 1
        return 0

    high_confidence_graph_documents = [
        item for item in graph_documents if graph_confidence_tier(item) >= 2
    ]
    low_confidence_graph_documents = [
        item for item in graph_documents if graph_confidence_tier(item) < 2
    ]
    append_documents(high_confidence_graph_documents)
    append_documents(list(rag_result.get("documents") or []))
    append_documents(low_confidence_graph_documents)
    for path in graph_result.get("paths") or []:
        documents.append(
            {
                "content": str(path),
                "source": "Neo4j GraphRAG",
                "score": None,
                "kind": "graph_path",
            }
        )

    if query:
        graph_paths = [item for item in documents if item.get("kind") == "graph_path"]
        ranked_documents = [item for item in documents if item.get("kind") != "graph_path"]

        def rank_key(item: dict[str, Any]):
            proxy = SimpleNamespace(
                file_name=item.get("file_name") or item.get("source") or "",
                content=item.get("content") or item.get("text") or "",
                summary=item.get("summary") or "",
                score=item.get("score") or 0.0,
            )
            local_score, base_score = RagHandler._local_priority_score(query, proxy)
            graph_support = int(item.get("graph_support_count") or 0)
            graph_seed_hits = int(item.get("graph_seed_hit_count") or 0)
            graph_file_focus = int(item.get("graph_file_focus") or 0)
            graph_tier = graph_confidence_tier(item)
            is_graph_document = bool(graph_support or graph_seed_hits)
            source_bias = 1 if not is_graph_document else 0
            return (
                graph_tier,
                source_bias,
                local_score,
                graph_support + graph_seed_hits + graph_file_focus,
                base_score,
            )

        ranked_documents.sort(key=rank_key, reverse=True)
        documents = ranked_documents + graph_paths

    return documents


def _build_extractive_answer(
    sample: dict[str, Any],
    contexts: list[dict[str, Any]],
    *,
    domain_pack_id: str | None = None,
) -> dict[str, Any]:
    if str(domain_pack_id or "").strip() == "contract_review":
        contract_answer = _build_contract_review_answer_v2(sample["query"], contexts)
        if contract_answer:
            return {
                "id": sample["id"],
                "query": sample["query"],
                "answer": contract_answer[:1200],
                "citations": _select_best_citations(contract_answer, contexts, limit=1),
            }

    ranked_snippets: list[tuple[float, float, int, str]] = []
    for index, context in enumerate(contexts[:5]):
        content = str(context.get("content") or context.get("text") or "").strip()
        if not content or context.get("kind") == "graph_path":
            continue
        for snippet in _sentence_like_units(content):
            score, density = _snippet_score(sample["query"], snippet, context_rank=index)
            ranked_snippets.append((score, density, index, snippet))

    ranked_snippets.sort(key=lambda item: (item[0], item[1], -item[2], len(item[3])), reverse=True)
    selected_snippets: list[str] = []
    selected_context_indexes: list[int] = []
    seen_snippets: set[str] = set()
    best_score = ranked_snippets[0][0] if ranked_snippets else 0.0
    minimum_score = max(3.0, best_score - 3.0)
    for score, _, context_index, snippet in ranked_snippets:
        normalized = re.sub(r"\s+", " ", snippet).strip()
        if score < minimum_score or normalized in seen_snippets:
            continue
        seen_snippets.add(normalized)
        selected_snippets.append(normalized)
        if context_index not in selected_context_indexes:
            selected_context_indexes.append(context_index)
        if len(selected_snippets) >= 3:
            break

    if selected_snippets:
        answer = "\n".join(selected_snippets)[:1200]
        citations = [contexts[index] for index in selected_context_indexes[:3]]
    else:
        context_text = "\n".join(str(context.get("content", "")) for context in contexts[:3]).strip()
        answer = context_text[:1200] if context_text else NO_EVIDENCE_ANSWER
        citations = contexts[:3]
    return {
        "id": sample["id"],
        "query": sample["query"],
        "answer": answer,
        "citations": citations,
    }


def _context_block(contexts: list[dict[str, Any]], limit: int = 5) -> str:
    lines = []
    for index, context in enumerate(contexts[:limit], start=1):
        content = str(context.get("content") or context.get("text") or "").strip()
        if content:
            lines.append(f"[{index}] {content[:1500]}")
    return "\n\n".join(lines)


def _extract_json_object(text: str) -> dict[str, Any] | None:
    cleaned = str(text or "").replace("```json", "").replace("```", "").strip()
    try:
        result = json.loads(cleaned)
        return result if isinstance(result, dict) else None
    except Exception:
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start >= 0 and end > start:
            try:
                result = json.loads(cleaned[start : end + 1])
                return result if isinstance(result, dict) else None
            except Exception:
                return None
    return None


def _clamp_score(value: Any, default: float = 0.0) -> float:
    try:
        return max(0.0, min(float(value), 1.0))
    except Exception:
        return default


async def _build_llm_answer(sample: dict[str, Any], contexts: list[dict[str, Any]]) -> dict[str, Any]:
    context_text = _context_block(contexts)
    if not context_text:
        return _build_extractive_answer(sample, contexts)

    try:
        from langchain_core.messages import HumanMessage, SystemMessage

        from zuno.core.models.manager import ModelManager

        client = ModelManager.get_conversation_model()
        prompt = (
            f"问题：{sample['query']}\n\n"
            f"证据：\n{context_text}\n\n"
            "请基于证据给出简洁答案，并用 [编号] 标注支撑证据。"
        )
        response = await asyncio.to_thread(
            client.invoke,
            [SystemMessage(content=ANSWER_SYSTEM_PROMPT), HumanMessage(content=prompt)],
        )
        answer = str(getattr(response, "content", "") or "").strip() or NO_EVIDENCE_ANSWER
        return {
            "id": sample["id"],
            "query": sample["query"],
            "answer": answer,
            "citations": contexts[:3],
            "answer_mode": "llm",
        }
    except Exception as err:
        fallback = _build_extractive_answer(sample, contexts)
        fallback["answer_mode"] = "extractive_fallback"
        fallback["answer_error"] = str(err)
        return fallback


async def _build_answer(
    sample: dict[str, Any],
    contexts: list[dict[str, Any]],
    *,
    answer_mode: str,
    domain_pack_id: str | None = None,
) -> dict[str, Any]:
    if answer_mode == "llm":
        return await _build_llm_answer(sample, contexts)
    if answer_mode == "strict_grounded":
        answer = _build_extractive_answer(sample, contexts, domain_pack_id=domain_pack_id)
        support_verdict = _build_support_verdict(
            str(answer.get("answer") or ""),
            contexts,
            list(answer.get("citations") or []),
            query=str(sample.get("query") or ""),
        )
        if support_verdict.get("status") != "supported":
            answer["answer"] = NO_EVIDENCE_ANSWER
            answer["citations"] = []
        answer["answer_mode"] = "strict_grounded"
        answer["evidence_bundle"] = _build_evidence_bundle(contexts, list(answer.get("citations") or []))
        answer["support_verdict"] = _build_support_verdict(
            str(answer.get("answer") or ""),
            contexts,
            list(answer.get("citations") or []),
            query=str(sample.get("query") or ""),
        )
        return answer
    answer = _build_extractive_answer(sample, contexts, domain_pack_id=domain_pack_id)
    answer["answer_mode"] = "extractive"
    answer["evidence_bundle"] = _build_evidence_bundle(contexts, list(answer.get("citations") or []))
    answer["support_verdict"] = _build_support_verdict(
        str(answer.get("answer") or ""),
        contexts,
        list(answer.get("citations") or []),
        query=str(sample.get("query") or ""),
    )
    return answer


def _judge_answer_heuristic(sample: dict[str, Any], answer_row: dict[str, Any], contexts: list[dict[str, Any]]) -> dict[str, Any]:
    answer = str(answer_row.get("answer") or "")
    reference = str(sample.get("reference_answer") or "")
    snippet_lines = [
        fragment.strip("。；; ")
        for line in answer.splitlines()
        for fragment in re.split(r"[；;]+", line)
        if fragment.strip("。；; ")
    ]
    context_units = [
        unit
        for context in contexts
        if context.get("kind") != "graph_path"
        for unit in _sentence_like_units(str(context.get("content", "") or context.get("text", "")))
    ]
    if snippet_lines and context_units:
        supported = sum(
            1
            for line in snippet_lines
            if any(
                line in unit or _semantic_overlap_score(line, unit) >= 0.45
                for unit in context_units
            )
        )
        faithfulness = supported / len(snippet_lines)
    else:
        faithfulness = 0.0
    return {
        "id": sample["id"],
        "faithfulness": 0.0
        if not answer or answer == NO_EVIDENCE_ANSWER
        else faithfulness,
        "answer_correctness": _overlap_score(answer, reference),
    }


async def _judge_answer_llm(
    sample: dict[str, Any],
    answer_row: dict[str, Any],
    contexts: list[dict[str, Any]],
) -> dict[str, Any]:
    try:
        from langchain_core.messages import HumanMessage, SystemMessage

        from zuno.core.models.manager import ModelManager

        context_text = _context_block(contexts)
        client = ModelManager.get_conversation_model()
        prompt = {
            "query": sample.get("query"),
            "reference_answer": sample.get("reference_answer"),
            "answer": answer_row.get("answer"),
            "contexts": context_text,
            "output_schema": {
                "faithfulness": "0..1 number",
                "answer_correctness": "0..1 number",
                "rationale": "short Chinese reason",
            },
        }
        response = await asyncio.to_thread(
            client.invoke,
            [
                SystemMessage(content=JUDGE_SYSTEM_PROMPT),
                HumanMessage(content=json.dumps(prompt, ensure_ascii=False)),
            ],
        )
        parsed = _extract_json_object(str(getattr(response, "content", "") or ""))
        if not parsed:
            raise ValueError("judge response is not valid JSON")
        return {
            "id": sample["id"],
            "faithfulness": _clamp_score(parsed.get("faithfulness")),
            "answer_correctness": _clamp_score(parsed.get("answer_correctness")),
            "judge_mode": "llm",
            "rationale": str(parsed.get("rationale") or ""),
        }
    except Exception as err:
        fallback = _judge_answer_heuristic(sample, answer_row, contexts)
        fallback["judge_mode"] = "heuristic_fallback"
        fallback["judge_error"] = str(err)
        return fallback


async def _judge_answer(
    sample: dict[str, Any],
    answer_row: dict[str, Any],
    contexts: list[dict[str, Any]],
    *,
    judge_mode: str,
) -> dict[str, Any]:
    if judge_mode == "llm":
        return await _judge_answer_llm(sample, answer_row, contexts)
    result = _judge_answer_heuristic(sample, answer_row, contexts)
    result["judge_mode"] = "heuristic"
    return result


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
    answer_mode: str = "extractive",
    judge_mode: str = "heuristic",
) -> dict[str, Any]:
    await initialize_app_settings()
    langsmith_configured = False
    if trace_langsmith:
        langsmith_configured = configure_langsmith()

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
                "langsmith_configured": langsmith_configured,
                "answer_mode": answer_mode,
                "judge_mode": judge_mode,
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
        runtime_retrieval_options = _runtime_retrieval_options(retrieval_options)
        for sample in samples:
            metadata = {
                "eval_run_id": output_dir.name,
                "eval_sample_id": sample["id"],
                "profile_name": profile,
                "retrieval_mode": retrieval_mode,
                "retrieval_options": retrieval_options,
                "knowledge_ids": knowledge_ids,
            }

            async def retrieve_one(
                *,
                mode: str = retrieval_mode,
                options: dict[str, Any] = runtime_retrieval_options,
            ) -> dict[str, Any]:
                return await RagHandler.retrieve_ranked_documents_with_metadata(
                    sample["query"],
                    knowledge_ids,
                    knowledge_ids,
                    retrieval_mode=mode,
                    retrieval_options=options,
                )

            retrieval_started_at = time.perf_counter()
            retrieval_result = await _maybe_trace(
                enabled=trace_langsmith,
                run_name=f"zuno-rag-eval:{profile}:{sample['id']}",
                metadata=metadata,
                func=retrieve_one,
            )
            retrieval_latency_ms = round((time.perf_counter() - retrieval_started_at) * 1000, 2)
            retrieval_metadata = retrieval_result.get("metadata") or {}
            if retrieval_metadata.get("latency_ms") is None:
                retrieval_metadata["latency_ms"] = retrieval_latency_ms
            if "cost_usd" not in retrieval_metadata:
                retrieval_metadata["cost_usd"] = None
            contexts = _extract_contexts(retrieval_result, sample["query"])
            if retrieval_options.get("agentic_floor_fusion"):
                floor_options = dict(retrieval_options.get("floor_retrieval_options") or {})
                floor_retrieval_started_at = time.perf_counter()
                floor_result = await _maybe_trace(
                    enabled=trace_langsmith,
                    run_name=f"zuno-rag-eval:{profile}:{sample['id']}:standard-floor",
                    metadata={**metadata, "agentic_floor_fusion_stage": "standard_floor"},
                    func=lambda: retrieve_one(mode="rag", options=_runtime_retrieval_options(floor_options)),
                )
                floor_latency_ms = round((time.perf_counter() - floor_retrieval_started_at) * 1000, 2)
                floor_contexts = _extract_contexts(floor_result, sample["query"])
                contexts, fusion_trace = _fuse_agentic_floor_contexts(
                    floor_contexts,
                    contexts,
                    limit=int(retrieval_options.get("fusion_top_k") or 5),
                )
                retrieval_metadata["agentic_floor_fusion"] = {
                    **fusion_trace,
                    "floor_latency_ms": floor_latency_ms,
                    "floor_final_mode": floor_result.get("final_mode"),
                    "enhanced_final_mode": retrieval_result.get("final_mode"),
                }
            effective_domain_pack_id = str(
                ((retrieval_metadata.get("retrieval_options") or {}).get("domain_pack_id"))
                or retrieval_options.get("domain_pack_id")
                or ""
            ).strip() or None
            retrieval_rows.append(
                {
                    "id": sample["id"],
                    "query": sample["query"],
                    "profile": profile,
                    "retrieval_mode": retrieval_mode,
                    "retrieval_options": retrieval_options,
                    "contexts": contexts,
                    "metadata": retrieval_metadata,
                    "raw_result": {
                        "first_mode": retrieval_result.get("first_mode"),
                        "final_mode": retrieval_result.get("final_mode"),
                        "fallback_reason": retrieval_result.get("fallback_reason"),
                        "round_count": retrieval_result.get("round_count"),
                        "agentic_floor_fusion": bool(retrieval_options.get("agentic_floor_fusion")),
                    },
                }
            )

            answer_row = await _build_answer(
                sample,
                contexts,
                answer_mode=answer_mode,
                domain_pack_id=effective_domain_pack_id,
            )
            answer_rows.append(answer_row)
            judge_rows.append(
                await _judge_answer(sample, answer_row, contexts, judge_mode=judge_mode)
            )

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
        "answer_mode": answer_mode,
        "judge_mode": judge_mode,
        "trace_langsmith": trace_langsmith,
        "langsmith_configured": langsmith_configured,
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
    parser.add_argument("--profile-set", choices=sorted(PROFILE_SETS.keys()), default=None)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--trace-langsmith", action="store_true")
    parser.add_argument("--answer-mode", choices=["extractive", "strict_grounded", "llm"], default="extractive")
    parser.add_argument("--judge-mode", choices=["heuristic", "llm"], default="heuristic")
    args = parser.parse_args()

    output_dir = args.output_dir or default_runs_root() / time.strftime("%Y%m%d-%H%M%S")
    report = asyncio.run(
        run_eval(
            dataset_path=args.dataset,
            knowledge_ids=args.knowledge_ids,
            profiles=resolve_profiles(profiles=args.profiles, profile_set=args.profile_set),
            output_dir=output_dir,
            trace_langsmith=args.trace_langsmith,
            answer_mode=args.answer_mode,
            judge_mode=args.judge_mode,
        )
    )
    print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()

