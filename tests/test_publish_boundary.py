from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_gitignore_covers_private_and_local_surfaces() -> None:
    content = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")

    required_entries = [
        ".agent/",
        ".agentmd",
        ".local/",
        "docs/superpowers/",
        "src/frontend/AGENTS.md",
        "infra/docker/docker_config.local.yaml",
        "src/backend/agentchat/config.local.yaml",
        "src/backend/agentchat/evals/rag_eval/corpus/",
        "src/backend/agentchat/evals/rag_eval/runs/",
    ]

    for entry in required_entries:
        assert entry in content, f"missing publish-boundary ignore: {entry}"


def test_public_docs_link_publish_boundary_and_structure_docs() -> None:
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    docs_index = (REPO_ROOT / "docs" / "README.md").read_text(encoding="utf-8")
    dev_docs = (
        REPO_ROOT / "docs" / "development" / "README.md"
    ).read_text(encoding="utf-8")

    assert "./docs/development/github-publish-boundary.md" in readme
    assert "./docs/development/README.md" in readme
    assert "./architecture/README.md" in docs_index
    assert "./development/README.md" in docs_index
    assert "backend-layering-guidelines.md" in dev_docs
    assert "github-publish-boundary.md" in dev_docs


def test_publish_boundary_doc_mentions_private_local_assets() -> None:
    content = (
        REPO_ROOT / "docs" / "development" / "github-publish-boundary.md"
    ).read_text(encoding="utf-8")

    required_phrases = [
        ".agent/",
        ".agentmd",
        ".local/",
        "docs/superpowers/",
        "apps/",
        "docs/",
        "infra/",
        "src/",
        "tests/",
        "tools/",
    ]

    for phrase in required_phrases:
        assert phrase in content, f"missing publish-boundary phrase: {phrase}"
