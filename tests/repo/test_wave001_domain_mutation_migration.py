from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MIGRATION = REPO_ROOT / "infra/db/alembic/versions/20260813_57_wave001_domain_mutation.py"


def test_wave001_migration_is_single_head_and_has_upgrade_downgrade() -> None:
    content = MIGRATION.read_text(encoding="utf-8")

    assert 'revision = "20260813_57"' in content
    assert 'down_revision = "20260729_56"' in content
    assert "def upgrade()" in content
    assert "def downgrade()" in content
    for table in (
        '"domain_aggregate_heads"',
        '"domain_mutation_records"',
        '"domain_state_versions"',
    ):
        assert table in content
    assert "uq_domain_mutation_idempotency" in content
    assert "uq_domain_state_version" in content
