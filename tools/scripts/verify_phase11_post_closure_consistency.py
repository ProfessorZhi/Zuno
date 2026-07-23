from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PROGRAM_ROOT = REPO_ROOT / ".agent" / "programs"
WORK_PRODUCTS = PROGRAM_ROOT / "work-products"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def verify_phase11_post_closure_consistency() -> list[str]:
    """PHASE11 is closed; this gate protects the completed boundary."""
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
        "phase file": ["status: completed", "Goal02", "implementation_available"],
        "readiness": [
            "current_phase_status: completed",
            "coordinator_approval: approved",
            "implementation_available: 80",
            "target_not_current: 0",
        ],
        "manifest": [
            "id: PHASE11",
            "state: completed",
            "id: PHASE08",
            "state: completed",
            "id: PHASE12",
            "state: ready",
        ],
        "current": ["current_phase: PHASE12", "PHASE11 completed", "PHASE12 ready"],
        "closure checklist": [
            "PHASE11 completed",
            "- [x] PHASE11 Durable Ingestion and Source Lineage",
        ],
        "production readiness": ["PHASE11 completed", "PHASE12 ready", "not production ready"],
        "coordinator closure": ["status: completed", "coordinator_approval: approved"],
    }
    for label, phrases in required.items():
        text = surfaces[label]
        for phrase in phrases:
            if phrase not in text:
                errors.append(f"{label} missing closed PHASE11 phrase: {phrase}")
    return errors


def main() -> int:
    errors = verify_phase11_post_closure_consistency()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("PHASE11 post-closure consistency gate failed.")
        return 1
    print("PHASE11 post-closure consistency gate passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
