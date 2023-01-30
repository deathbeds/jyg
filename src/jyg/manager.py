"""Manage the remote Jupyter App commands."""
import asyncio
from typing import TYPE_CHECKING, Any, Tuple

import traitlets as T
from traitlets.config import LoggingConfigurable

if TYPE_CHECKING:  # pragma: no cover
    from .handlers import CommandWebSocketHandler

from . import constants as C


class CommandManager(LoggingConfigurable):
    """A manager for remote Jupyter App commands."""

    handlers: Tuple["CommandWebSocketHandler", ...] = T.Tuple().tag(config=False)

    def subscribe(self, handler: "CommandWebSocketHandler") -> None:
        """Subscribe to an app."""
        self.log.debug("handler subscribed %s", handler)
        self.handlers += (*self.handlers, handler)

    def unsubscribe(self, handler: "CommandWebSocketHandler") -> None:
        """Unsubscribe from an app."""
        self.log.debug("handler unsubscribed %s", handler)
        self.handlers = tuple(h for h in self.handlers if h != handler)

    async def get_apps(self) -> Tuple[Any, ...]:
        """Get all info from subscribed apps."""
        return tuple(
            await asyncio.gather(
                *[handler.jyg_request(C.APP_INFO) for handler in self.handlers]
            )
        )

    async def run(self, command_id: str, args: Any) -> Any:
        """Run a command."""
        self.log.debug("execute requested %s %s", command_id, args)
        # TODO: handle multiple apps
        if not self.handlers:
            return {"error": "no handlers"}

        handler = self.handlers[0]

        return await handler.jyg_request(C.RUN, {"id": command_id, "args": args})
