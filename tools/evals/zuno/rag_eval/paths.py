from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
LOCAL_AGENTCHAT_ROOT = REPO_ROOT / ".local" / "evals" / "agentchat" / "rag_eval"
LOCAL_CORPUS_ROOT = LOCAL_AGENTCHAT_ROOT / "corpus"
LOCAL_RUNS_ROOT = LOCAL_AGENTCHAT_ROOT / "runs"


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
]
