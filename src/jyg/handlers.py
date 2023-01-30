"""Tornado handlers for jyg."""
import asyncio
from typing import TYPE_CHECKING, Any, Dict, cast
from uuid import uuid4

from jupyter_server.base.handlers import APIHandler, JupyterHandler
from jupyter_server.base.zmqhandlers import WebSocketHandler, WebSocketMixin
from jupyter_server.serverapp import ServerApp
from jupyter_server.utils import url_path_join as ujoin
from tornado.escape import json_decode

from .schema import msg_v0 as M

if TYPE_CHECKING:  # pragma: no cover
    from .manager import CommandManager


class CommandListHandler(APIHandler):
    """List commands."""

    command_manager: "CommandManager"

    def initialize(
        self, command_manager: "CommandManager", *args: Any, **kwargs: Any
    ) -> None:
        """Prepare the handler."""
        self.command_manager = command_manager
        super().initialize(*args, **kwargs)

    async def get(self) -> None:
        """Get the information about running/known apps."""
        apps = await self.command_manager.get_apps()
        self.write({"apps": apps})


class CommandHandler(APIHandler):
    """Handle request for a single command."""

    command_manager: "CommandManager"

    def initialize(
        self, command_manager: "CommandManager", *args: Any, **kwargs: Any
    ) -> None:
        """Prepare the handler."""
        self.command_manager = command_manager
        super().initialize(*args, **kwargs)

    async def get(self, command_id: str) -> None:
        """Get the information about a single command."""
        apps = await self.command_manager.get_apps()
        # TODO: handle multiple apps
        if not apps:
            self.set_status(404)
            self.write({"error": "no apps found"})
            return
        app = apps[0]
        if command_id not in app["commands"]:
            self.set_status(404)
            self.write({"error": "command not found"})
            return
        self.write(app["commands"][command_id])

    async def post(self, command_id: str) -> None:
        """Run a single command."""
        args = json_decode(self.request.body)
        result = await self.command_manager.run(command_id, args)
        self.write({"response": result})


class CommandWebSocketHandler(WebSocketMixin, WebSocketHandler, JupyterHandler):  # type: ignore
    """Handle bidrectional communication with a JupyterApp."""

    _responses: Dict[str, "asyncio.Future[M.AnyResponse]"]

    command_manager: "CommandManager"

    def initialize(
        self, command_manager: "CommandManager", *args: Any, **kwargs: Any
    ) -> None:
        """Prepare the handler."""
        self._responses = {}
        self.command_manager = command_manager
        if hasattr(super(), "initialize"):
            super().initialize(*args, **kwargs)

    def open(self, *args: str, **kwargs: str) -> None:
        """Handle a new websocket."""
        super().open(*args, **kwargs)
        self.command_manager.subscribe(self)

    async def on_message(self, raw_message: Any) -> None:
        """Handle a WebSocket message from the client."""
        message: M.AnyResponse = json_decode(raw_message)
        request_id = message["request_id"]
        request = self._responses.pop(request_id)
        request.set_result(message)

    def on_close(self) -> None:
        """Handle the WebSocket closing."""
        self.command_manager.unsubscribe(self)

    async def jyg_request(
        self, request_type: M.AnyMessageType, content: M.AnyContent = None
    ) -> Any:
        """Make a jyg request and wait for the response."""
        request_id = str(uuid4())
        request = dict(
            request_id=request_id,
            request_type=str(request_type),
            content=content or {},
        )
        self._responses[request_id] = asyncio.Future()
        self.write_message(request)
        response = await self._responses[request_id]
        if "error" in response:
            return {"error": cast(M.ErrorResponse, response)["error"]}
        else:
            return cast(M.AnyValidResponse, response)["content"]


def add_handlers(nbapp: ServerApp, command_manager: "CommandManager") -> None:
    """Add Command routes to the notebook server web application."""
    jyg_url = ujoin(nbapp.base_url, "jyg")
    re_command = "(?P<command_id>.+)"

    opts = {"command_manager": command_manager}

    nbapp.web_app.add_handlers(
        ".*",
        [
            (ujoin(jyg_url, "commands"), CommandListHandler, opts),
            (ujoin(jyg_url, "commands", re_command), CommandHandler, opts),
            (ujoin(jyg_url, "ws"), CommandWebSocketHandler, opts),
        ],
    )
