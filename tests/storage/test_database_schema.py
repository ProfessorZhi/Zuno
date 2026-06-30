from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src" / "backend"))


def test_pipeline_tables_are_registered_in_sqlmodel_metadata():
    from sqlmodel import SQLModel
    import zuno.platform.database  # noqa: F401

    assert "knowledge_task" in SQLModel.metadata.tables
    assert "knowledge_task_event" in SQLModel.metadata.tables
    assert "memory_raw_event" in SQLModel.metadata.tables
    assert "memory_task_summary" in SQLModel.metadata.tables
    assert "memory_candidate" in SQLModel.metadata.tables
    assert "memory_review_decision" in SQLModel.metadata.tables
    assert "memory_governance_ledger" in SQLModel.metadata.tables
