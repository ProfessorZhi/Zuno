import importlib
import pkgutil

from sqlmodel import SQLModel

from agentchat.database import models as model_package


def import_all_models() -> None:
    for module_info in pkgutil.iter_modules(model_package.__path__):
        if module_info.name.startswith("_"):
            continue
        importlib.import_module(f"{model_package.__name__}.{module_info.name}")


import_all_models()
metadata = SQLModel.metadata
