RETRIEVAL_MODES = {
    "default",
    "rag",
    "standard_retrieval",
    "graphrag",
    "hybrid",
    "hybrid_rag",
    "rag_graph",
    "rag_graph_deep",
    "enhanced_retrieval",
    "local_graphrag",
    "community_global",
    "drift_like",
    "auto",
}


def normalize_retrieval_mode(mode: str | None) -> str:
    normalized = (mode or "auto").strip().lower()
    if normalized not in RETRIEVAL_MODES:
        return "auto"
    if normalized == "rag_graph":
        return "rag_graph_deep"
    if normalized == "standard_retrieval":
        return "rag"
    if normalized == "enhanced_retrieval":
        return "rag_graph_deep"
    if normalized == "hybrid":
        return "hybrid_rag"
    if normalized == "graphrag":
        return "local_graphrag"
    if normalized == "default":
        return "auto"
    return normalized
