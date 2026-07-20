from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_verifier():
    module_path = REPO_ROOT / "tools/scripts/verify_repo_structure.py"
    spec = importlib.util.spec_from_file_location("verify_repo_structure", module_path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _write(path: Path, text: str = "ok") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _minimal_repo(root: Path, verifier) -> None:
    for relative_path in verifier.REQUIRED_PATHS:
        _write(root / relative_path)
    for relative_dir in ["docs/architecture", ".agent/architecture"]:
        for name in verifier.ARCHITECTURE_ALLOWED_FILES:
            _write(root / relative_dir / name)
    _write(
        root / ".agent/programs/current.md",
        "\n".join(
            [
                "state: active",
                f"active_program: {verifier.ACTIVE_PROGRAM_NAME}",
                "current_phase: PHASE08",
            ]
        ),
    )
    _write(
        root / ".agent/programs/program-manifest.yaml",
        "\n".join(
            [
                "program:",
                f"  id: {verifier.ACTIVE_PROGRAM_NAME}",
                "  state: active",
                "  current_phase: PHASE08",
                "  phase_count: 22",
            ]
        ),
    )
    for name in verifier.ARCHIVED_PROGRAM_REQUIRED_FILES:
        _write(root / "docs/history/programs/archived-program-v1" / name)
    _write(root / "docs/architecture/README.md", "canonical architecture four-file set")


def test_current_legal_structure_passes() -> None:
    verifier = _load_verifier()
    assert verifier.run_verification().ok


def test_architecture_extra_file_fails(tmp_path, monkeypatch) -> None:
    verifier = _load_verifier()
    _minimal_repo(tmp_path, verifier)
    _write(tmp_path / "docs/architecture/production-readiness.md")
    monkeypatch.setattr(verifier, "REPO_ROOT", tmp_path)

    errors = verifier.verify_architecture_directory_contract()

    assert any("docs/architecture contains non-canonical files" in error for error in errors)


def test_active_program_route_drift_fails(tmp_path, monkeypatch) -> None:
    verifier = _load_verifier()
    _minimal_repo(tmp_path, verifier)
    _write(
        tmp_path / ".agent/programs/current.md",
        "\n".join(
            [
                "state: active",
                "active_program: zuno-old-program-v1",
                "current_phase: PHASE08",
            ]
        ),
    )
    monkeypatch.setattr(verifier, "REPO_ROOT", tmp_path)

    errors = verifier.verify_active_program_contract()

    assert any(verifier.ACTIVE_PROGRAM_NAME in error for error in errors)


def test_history_archive_missing_required_file_fails(tmp_path, monkeypatch) -> None:
    verifier = _load_verifier()
    _minimal_repo(tmp_path, verifier)
    (tmp_path / "docs/history/programs/archived-program-v1/README.md").unlink()
    monkeypatch.setattr(verifier, "REPO_ROOT", tmp_path)

    errors = verifier.verify_history_program_archives()

    assert any("history program archive incomplete" in error for error in errors)
