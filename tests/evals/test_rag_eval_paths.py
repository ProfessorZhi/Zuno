from pathlib import Path

from tools.evals.zuno.rag_eval.paths import (
    LOCAL_AGENTCHAT_ROOT,
    REPO_ROOT,
    default_corpus_root,
    default_runs_root,
    resolve_local_artifact_path,
)


def test_explicit_local_artifact_paths_are_anchored_to_repository_root() -> None:
    assert resolve_local_artifact_path(Path(".local")) == REPO_ROOT / ".local"
    assert resolve_local_artifact_path(
        Path(".local/evals/zuno/rag_eval/runs/direct-manifest-test")
    ) == REPO_ROOT / ".local" / "evals" / "zuno" / "rag_eval" / "runs" / "direct-manifest-test"


def test_non_local_relative_paths_and_absolute_paths_keep_their_meaning(tmp_path) -> None:
    relative = Path("runs/eval-output")
    absolute = tmp_path / "eval-output"

    assert resolve_local_artifact_path(relative) == relative
    assert resolve_local_artifact_path(absolute) == absolute


def test_default_eval_roots_have_one_local_namespace() -> None:
    for path in (LOCAL_AGENTCHAT_ROOT, default_corpus_root(), default_runs_root()):
        assert path.is_relative_to(REPO_ROOT)
        assert ".local/.local" not in path.as_posix()
