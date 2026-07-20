from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PROGRAM_ROOT = REPO_ROOT / ".agent" / "programs"
WORK_PRODUCTS = PROGRAM_ROOT / "work-products"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def verify_phase11_post_closure_consistency() -> list[str]:
    """PHASE11 is reopened; this gate now protects against stale completed claims."""
    errors: list[str] = []
    surfaces = {
        "phase file": _read(PROGRAM_ROOT / "PHASE11_durable-ingestion-and-source-lineage.md"),
        "readiness": _read(WORK_PRODUCTS / "phase11-readiness.yaml"),
        "manifest": _read(PROGRAM_ROOT / "program-manifest.yaml"),
        "current": _read(PROGRAM_ROOT / "current.md"),
        "closure checklist": _read(PROGRAM_ROOT / "closure-checklist.md"),
        "production readiness": _read(REPO_ROOT / "docs/status/production-readiness.md"),
        "coordinator closure": _read(REPO_ROOT / "docs/evidence/phase11-coordinator-closure.md"),
    }
    required = {
        "phase file": ["status: in_progress", "Goal01 audit"],
        "readiness": [
            "current_phase_status: in_progress",
            "coordinator_approval: pending_reopened",
            "target_not_current: 80",
        ],
        "manifest": [
            "id: PHASE11",
            "state: in_progress",
            "id: PHASE08",
            "state: ready",
            "id: PHASE12",
            "state: planned",
        ],
        "current": ["PHASE11 reopened/in_progress", "PHASE08 仍 ready", "PHASE12 仍 planned"],
        "closure checklist": [
            "PHASE11 reopened in_progress",
            "- [ ] PHASE11 Durable Ingestion and Source Lineage",
        ],
        "production readiness": ["PHASE11 reopened/in_progress", "PHASE08 ready", "PHASE12 仍 planned"],
        "coordinator closure": ["status: reopened", "coordinator_approval: pending_reopened"],
    }
    for label, phrases in required.items():
        text = surfaces[label]
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{label} missing reopened PHASE11 phrase: {phrase}")
    return errors


def main() -> int:
    errors = verify_phase11_post_closure_consistency()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE11 reopened consistency gate failed.")
        return 1
    print("PHASE11 reopened consistency gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
