RETRIEVAL_MODES = {"default", "rag", "graphrag", "hybrid", "auto"}


def normalize_retrieval_mode(mode: str | None) -> str:
    normalized = (mode or "default").strip().lower()
    if normalized not in RETRIEVAL_MODES:
        return "default"
    return normalized
