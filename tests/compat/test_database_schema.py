from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "services" / "api" / "src"))


def test_pipeline_tables_are_registered_in_sqlmodel_metadata():
    from sqlmodel import SQLModel
    import agentchat.database  # noqa: F401

    assert "knowledge_task" in SQLModel.metadata.tables
    assert "knowledge_task_event" in SQLModel.metadata.tables
