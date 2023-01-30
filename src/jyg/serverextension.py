"""Serverextension for jyg."""
from jupyter_server.serverapp import ServerApp
from traitlets import Instance

from .handlers import add_handlers
from .manager import CommandManager


def load_jupyter_server_extension(nbapp: ServerApp) -> None:
    """Create a CommandManager and add handlers."""
    manager = CommandManager(parent=nbapp)
    add_handlers(nbapp, manager)
    nbapp.add_traits(command_manager=Instance(CommandManager, default_value=manager))
