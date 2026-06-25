import importlib
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_domain_pack_runtime_service_source_is_retired_from_current_backend():
    assert not (REPO_ROOT / "src/backend/zuno/services/domain_pack").exists()


def test_domain_pack_runtime_service_import_stays_retired():
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("zuno.services.domain_pack")

    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("zuno.services.domain_pack.loader")
