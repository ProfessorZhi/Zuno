from pathlib import Path

import yaml


def test_config_uses_database_section_with_postgresql_urls():
    config_path = Path(__file__).resolve().parents[1] / "config.yaml"
    with config_path.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    assert "database" in config
    assert config["database"]["sync_endpoint"].startswith("postgresql+psycopg://")
    assert config["database"]["async_endpoint"].startswith("postgresql+asyncpg://")
