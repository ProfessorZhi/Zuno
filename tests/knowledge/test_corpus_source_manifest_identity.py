"""PHASE22 GAP-B3 canonical corpus + source manifest identity tests
(Tasks F/G).

validate_canonical_corpus_identity() must validate the SOURCE manifest
for real (count, paths, hashes, document ids, tenant/workspace
consistency, 1:1 documents, chunk documents, manifest hash, canonical IR
binding, exact corpus files) and record the five hash identities
separately — never conflated.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from zuno.knowledge.indexing import (
    CorpusInputIdentityError,
    validate_canonical_corpus_identity,
)

ROOT = Path(__file__).resolve().parents[2]
TRACK_DIR = ROOT / "docs" / "evidence" / "goal05-phase22-machine-attested-synthetic-regression"
CORPUS_DIR = TRACK_DIR / "candidate-dataset" / "corpus"

DATASET_CORPUS_HASH = "749b932786416ea0c4fd35effa0e0bc6722ab5acc300fe1dde3cb7549d5b50e4"
SOURCE_MANIFEST_HASH = "0a6ee33cae62e5c3370217f5ec028a4efd1a52855557a71b57f2dc8bdce0c26a"
CANONICAL_IR_HASH = "43d4842d41ea528cec6bfdfd7540a0c58c8c6653f8fa752b9eee31c7a0f079a6"


def _load() -> tuple[dict, dict, dict[str, str]]:
    source_manifest = json.loads((TRACK_DIR / "source_upload_manifest.json").read_text(encoding="utf-8"))
    canonical_ir = json.loads((TRACK_DIR / "canonical_ir_manifest.json").read_text(encoding="utf-8"))
    from tools.evals.zuno.synthetic_benchmark.dataset_contract import sha256_json

    texts: dict[str, str] = {}
    hashes_by_text: dict[str, str] = {}
    for path in sorted(CORPUS_DIR.glob("*.md")):
        for paragraph in [chunk.strip() for chunk in path.read_text(encoding="utf-8").split("\n\n") if chunk.strip()]:
            hashes_by_text.setdefault(sha256_json({"text": paragraph}), paragraph)
    for chunk in canonical_ir["chunks"]:
        texts[chunk["chunk_id"]] = hashes_by_text[chunk["text_hash"]]
    return source_manifest, canonical_ir, texts


def test_identity_passes_on_the_real_frozen_manifests() -> None:
    source_manifest, canonical_ir, texts = _load()
    payload = validate_canonical_corpus_identity(
        source_manifest=source_manifest,
        canonical_ir_manifest=canonical_ir,
        corpus_root=CORPUS_DIR,
        manifest_chunk_texts=texts,
        dataset_corpus_hash=DATASET_CORPUS_HASH,
    )
    assert payload.document_count == 8
    assert payload.chunk_count == 24
    assert payload.input_kind == "frozen_candidate_manifest"
    assert payload.not_owner_produced is True
    for check_name in [
        "source_count_8",
        "source_paths_exist",
        "source_hashes_match",
        "documents_one_to_one",
        "chunk_documents_exist",
        "source_manifest_hash_valid",
        "canonical_ir_binds_source_manifest",
        "corpus_files_exact",
        "document_count_equal",
        "chunk_count_equal",
        "chunk_id_set_equal",
        "chunk_hashes_all_equal",
    ]:
        assert payload.identity_checks.get(check_name) is True, check_name


def test_five_hash_identities_are_separated() -> None:
    source_manifest, canonical_ir, texts = _load()
    payload = validate_canonical_corpus_identity(
        source_manifest=source_manifest,
        canonical_ir_manifest=canonical_ir,
        corpus_root=CORPUS_DIR,
        manifest_chunk_texts=texts,
        dataset_corpus_hash=DATASET_CORPUS_HASH,
    )
    hashes = {
        "dataset_corpus_hash": payload.dataset_corpus_hash,
        "source_manifest_hash": payload.source_manifest_hash,
        "canonical_ir_hash": payload.canonical_ir_hash,
        "content_set_hash": payload.content_set_hash,
    }
    assert hashes["dataset_corpus_hash"] == DATASET_CORPUS_HASH
    assert hashes["source_manifest_hash"] == SOURCE_MANIFEST_HASH
    assert hashes["canonical_ir_hash"] == CANONICAL_IR_HASH
    assert len(hashes["content_set_hash"]) == 64
    # The three manifest-level hashes are distinct (never conflated).
    assert len({hashes["dataset_corpus_hash"], hashes["source_manifest_hash"], hashes["canonical_ir_hash"]}) == 3


def test_content_set_hash_is_deterministic_from_24_chunks() -> None:
    source_manifest, canonical_ir, texts = _load()
    first = validate_canonical_corpus_identity(
        source_manifest=source_manifest,
        canonical_ir_manifest=canonical_ir,
        corpus_root=CORPUS_DIR,
        manifest_chunk_texts=texts,
        dataset_corpus_hash=DATASET_CORPUS_HASH,
    )
    second = validate_canonical_corpus_identity(
        source_manifest=source_manifest,
        canonical_ir_manifest=canonical_ir,
        corpus_root=CORPUS_DIR,
        manifest_chunk_texts=texts,
        dataset_corpus_hash=DATASET_CORPUS_HASH,
    )
    assert first.content_set_hash == second.content_set_hash
    assert first.chunk_count == 24 and len(first.chunk_ids) == 24


def test_identity_rejects_extra_corpus_file(tmp_path: Path) -> None:
    source_manifest, canonical_ir, texts = _load()
    (tmp_path / "extra_document.md").write_text("# Extra\n", encoding="utf-8")
    for path in sorted(CORPUS_DIR.glob("*.md")):
        (tmp_path / path.name).write_bytes(path.read_bytes())
    with pytest.raises(CorpusInputIdentityError) as exc:
        validate_canonical_corpus_identity(
            source_manifest=source_manifest,
            canonical_ir_manifest=canonical_ir,
            corpus_root=tmp_path,
            manifest_chunk_texts=texts,
            dataset_corpus_hash=DATASET_CORPUS_HASH,
        )
    assert "corpus_files_exact" in str(exc.value)


def test_identity_rejects_tampered_source_hash(tmp_path: Path) -> None:
    import copy

    source_manifest, canonical_ir, texts = _load()
    tampered = copy.deepcopy(source_manifest)
    tampered["sources"][0]["source_hash"] = "0" * 64
    with pytest.raises(CorpusInputIdentityError) as exc:
        validate_canonical_corpus_identity(
            source_manifest=tampered,
            canonical_ir_manifest=canonical_ir,
            corpus_root=CORPUS_DIR,
            manifest_chunk_texts=texts,
            dataset_corpus_hash=DATASET_CORPUS_HASH,
        )
    assert "source_hashes_match" in str(exc.value) or "source_hash" in str(exc.value)


def test_identity_rejects_canonical_ir_not_binding_source_manifest(tmp_path: Path) -> None:
    import copy

    source_manifest, canonical_ir, texts = _load()
    tampered_ir = copy.deepcopy(canonical_ir)
    tampered_ir["source_manifest_hash"] = "0" * 64
    with pytest.raises(CorpusInputIdentityError) as exc:
        validate_canonical_corpus_identity(
            source_manifest=source_manifest,
            canonical_ir_manifest=tampered_ir,
            corpus_root=CORPUS_DIR,
            manifest_chunk_texts=texts,
            dataset_corpus_hash=DATASET_CORPUS_HASH,
        )
    assert "canonical_ir_binds_source_manifest" in str(exc.value)


def test_identity_rejects_missing_chunk_text() -> None:
    source_manifest, canonical_ir, _texts = _load()
    missing = dict(_texts)
    missing.pop(next(iter(missing)))
    with pytest.raises(CorpusInputIdentityError):
        validate_canonical_corpus_identity(
            source_manifest=source_manifest,
            canonical_ir_manifest=canonical_ir,
            corpus_root=CORPUS_DIR,
            manifest_chunk_texts=missing,
            dataset_corpus_hash=DATASET_CORPUS_HASH,
        )
