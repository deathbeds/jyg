"""Main entrypoint for jyg."""

from typing import Dict, List

from ._version import __js__, __package_json__, __version__

__all__ = [
    "__version__",
    "_jupyter_labextension_paths",
    "_jupyter_server_extension_paths",
]


def _jupyter_labextension_paths() -> List[Dict[str, str]]:
    """Fetch the paths to JupyterLab extensions."""
    return [dict(src=(str(__package_json__.parent)), dest=__js__["name"])]


def _jupyter_server_extension_paths() -> List[Dict[str, str]]:
    """Fetch the paths to Jupyter Server extensions."""
    return [{"module": "jyg.serverextension"}]
