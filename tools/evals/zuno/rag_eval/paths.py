from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
LOCAL_AGENTCHAT_ROOT = REPO_ROOT / ".local" / "evals" / "zuno" / "rag_eval"
LOCAL_CORPUS_ROOT = LOCAL_AGENTCHAT_ROOT / "corpus"
LOCAL_RUNS_ROOT = LOCAL_AGENTCHAT_ROOT / "runs"


def resolve_local_artifact_path(path: Path) -> Path:
    """Anchor explicit ``.local/...`` paths to the repository root.

    Eval commands are sometimes launched from inside ``.local``.  Resolving a
    relative ``.local/...`` argument against the process working directory in
    that case creates ``.local/.local/...``.  The local artifact namespace is
    repository-owned, so only paths that explicitly enter that namespace are
    anchored here; other relative paths retain their caller-defined meaning.
    """
    candidate = Path(path)
    if candidate.is_absolute() or not candidate.parts:
        return candidate
    if candidate.parts[0].lower() == ".local":
        return REPO_ROOT.joinpath(*candidate.parts)
    return candidate


def default_corpus_root() -> Path:
    return LOCAL_CORPUS_ROOT


def default_runs_root() -> Path:
    return LOCAL_RUNS_ROOT


__all__ = [
    "LOCAL_AGENTCHAT_ROOT",
    "LOCAL_CORPUS_ROOT",
    "LOCAL_RUNS_ROOT",
    "default_corpus_root",
    "default_runs_root",
    "resolve_local_artifact_path",
]
