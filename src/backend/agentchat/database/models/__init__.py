from pathlib import Path
from pkgutil import extend_path

from zuno.database.models.agent import AgentTable

__path__ = extend_path(__path__, __name__)

_PACKAGE_ROOT = Path(__file__).resolve().parent
_ZUNO_MODELS_ROOT = _PACKAGE_ROOT.parents[2] / "zuno" / "database" / "models"
if _ZUNO_MODELS_ROOT.exists():
    zuno_models_root = str(_ZUNO_MODELS_ROOT)
    if zuno_models_root not in __path__:
        __path__.append(zuno_models_root)

__all__ = ["AgentTable"]
