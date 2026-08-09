from __future__ import annotations

from pathlib import Path


def test_graphrag_download_prepares_questions_and_official_textbook_corpus(
    tmp_path: Path, monkeypatch
) -> None:
    import tools.evals.zuno.rag_eval.datasets.download_public_datasets as downloader

    monkeypatch.setattr(downloader, "REPO_ROOT", tmp_path)

    def fake_fetch(url: str) -> bytes:
        if "/questions/OE.jsonl" in url:
            return b'{"Question":"q","Answer":"a"}\n' * 100
        return b"# Official GraphRAG textbook\n" * 100

    monkeypatch.setattr(downloader, "fetch_url_bytes", fake_fetch)

    result = downloader.download_microsoft_graphrag(tmp_path / "cache")

    assert result["source_id"] == "microsoft_graphrag_benchmarking"
    assert len(result["files"]) == 21
    assert Path(result["file"]).name == "questions.jsonl"
    assert len(result["corpus_files"]) == 20
    assert all((tmp_path / "cache" / rel).exists() for rel in [
        "questions.jsonl",
        *downloader.GRAPH_RAG_TEXTBOOK_FILES,
    ])

    def unexpected_fetch(url: str) -> bytes:
        raise AssertionError(f"cache miss during idempotent rerun: {url}")

    monkeypatch.setattr(downloader, "fetch_url_bytes", unexpected_fetch)
    rerun = downloader.download_microsoft_graphrag(tmp_path / "cache")
    assert rerun["files"] == result["files"]
