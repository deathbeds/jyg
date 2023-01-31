"""Serverextension for jyg."""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from jupyter_server.serverapp import ServerApp

__all__ = ["_load_jupyter_server_extension", "load_jupyter_server_extension"]


def _load_jupyter_server_extension(nbapp: "ServerApp") -> None:
    """Create a CommandManager and add handlers."""
    from traitlets import Instance

    from .handlers import add_handlers
    from .manager import CommandManager

    manager = CommandManager(parent=nbapp)
    add_handlers(nbapp, manager)
    nbapp.add_traits(command_manager=Instance(CommandManager, default_value=manager))


# for backwards compatibility
load_jupyter_server_extension = _load_jupyter_server_extension
