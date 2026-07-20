from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
VERIFY_UTF8 = REPO_ROOT / "tools" / "scripts" / "verify_utf8_doc_encoding.py"


def _load_verifier():
    spec = spec_from_file_location("verify_utf8_doc_encoding", VERIFY_UTF8)
    assert spec is not None
    assert spec.loader is not None
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_active_goal01_documents_are_valid_utf8_without_mojibake() -> None:
    verifier = _load_verifier()
    assert verifier.verify_utf8_doc_encoding() == []


def test_normal_chinese_document_passes(tmp_path, monkeypatch) -> None:
    verifier = _load_verifier()
    sample = tmp_path / "normal.md"
    sample.write_text("正常中文文档：状态、边界、证据。", encoding="utf-8")
    monkeypatch.setattr(verifier, "REPO_ROOT", tmp_path)

    assert verifier.verify_utf8_doc_encoding(["normal.md"]) == []


def test_mojibake_document_fails(tmp_path, monkeypatch) -> None:
    verifier = _load_verifier()
    sample = tmp_path / "broken.md"
    sample.write_text("乱码样本：鏈枃 銆 鐨 锛", encoding="utf-8")
    monkeypatch.setattr(verifier, "REPO_ROOT", tmp_path)

    issues = verifier.verify_utf8_doc_encoding(["broken.md"])

    assert issues
    assert "possible mojibake tokens" in issues[0].reason
