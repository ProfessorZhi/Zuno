from __future__ import annotations
import sys
from pathlib import Path
curr = Path(__file__).resolve()
while curr.name != "Zuno" and curr.parent != curr:
    curr = curr.parent
ROOT_DIR = curr
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
LOCAL_AGENTCHAT_ROOT = REPO_ROOT / ".local" / "evals" / "zuno" / "rag_eval"
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
