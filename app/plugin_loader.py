import importlib
import pkgutil
from logging import getLogger
from typing import Iterable

from django.core.exceptions import AppRegistryNotReady

logger = getLogger(__file__)


def load_plugins(plugin_path: str) -> Iterable[str]:
    """

    """
    result = []
    try:
        module = importlib.import_module(plugin_path)
        for finder, name, ispkg in pkgutil.iter_modules(module.__path__):
            if ispkg:
                try:
                    pkgutil.get_data(f"{plugin_path}.{name}", "plugin.py")
                    result.append(f"{plugin_path}.{name}")
                except FileNotFoundError as error:
                    logger.warning(f"Encountered an error determining if {name} is a plugin", exc_info=error)
                except AppRegistryNotReady as error:
                    logger.warning(f"Encountered an error determining if {name} is a plugin", exc_info=error)
        return result
    except Exception as error:
        logger.warning("Encountered an error while searching for plugins", exc_info=error)
    return []
