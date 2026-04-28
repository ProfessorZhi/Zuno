RETRIEVAL_MODES = {"default", "rag", "graphrag", "hybrid", "auto"}


def normalize_retrieval_mode(mode: str | None) -> str:
    normalized = (mode or "auto").strip().lower()
    if normalized not in RETRIEVAL_MODES:
        return "auto"
    if normalized == "default":
        return "auto"
    return normalized
