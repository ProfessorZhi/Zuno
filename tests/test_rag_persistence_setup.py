from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_backend_compose_persists_chroma_vector_db():
    compose_text = (REPO_ROOT / "docker" / "docker-compose.yml").read_text(encoding="utf-8")

    assert "/app/vector_db" in compose_text
    assert "backend_vector_db:" in compose_text
