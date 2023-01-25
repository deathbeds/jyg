"""Command line apps for jyg."""
import asyncio
from typing import Any, Dict, List

import traitlets as T
from jupyter_core.application import JupyterApp
from tornado import httpclient
from tornado.escape import json_decode, json_encode

from ._version import __version__
from .utils import parse_command_args


class _BaseApp(JupyterApp):
    """A base app for jyg."""

    version = __version__

    name: str = T.Unicode("jyg").tag(config=False)
    description: str = T.Unicode("a jyg application").tag(config=False)


class _AsyncApp(_BaseApp):
    """An ascyn app for jyg."""

    _client: httpclient.AsyncHTTPClient = T.Instance(httpclient.AsyncHTTPClient).tag(
        config=False
    )
    running_servers: List[Dict[str, Any]] = T.List().tag(config=False)

    @T.default("_client")
    def _default_client(self):
        """Get a client."""
        return httpclient.AsyncHTTPClient()

    def start_async(self):  # pragma: no cover
        """Start the asynchronous activities.

        Must be overridden in subclasses.
        """
        raise NotImplementedError(
            f"""{self.__class__} does not implement start_async"""
        )

    @T.default("running_servers")
    def _default_running_servers(self) -> List[Dict[str, Any]]:
        """Get running jupyter servers."""
        from jupyter_server.serverapp import list_running_servers

        return [*list_running_servers()]

    def jyg_url(self, *bits: str):
        """Get the jyg API URL."""
        from jupyter_server.utils import url_path_join as ujoin

        # TODO: handle multiple servers
        server = self.running_servers[0]
        return ujoin(server["url"], "jyg", *bits) + f"""?token={server["token"]}"""

    async def jyg_request(self, *bits, **fetch_kwargs):
        """Make a jyg request."""
        url = self.jyg_url(*bits)
        response = await self._client.fetch(url, **fetch_kwargs)
        # TODO: use header
        return json_decode(response.body)

    def start(self):
        """Start the loop and run the start_async method."""
        asyncio.get_event_loop().run_until_complete(self.start_async())


class JygListApp(_AsyncApp):
    """List jupyter app commands."""

    async def start_async(self):
        """Fetch the app info from a running jupyter app."""
        response = await self.jyg_request("commands")
        # TODO: handle multiple apss
        app = response["apps"][0]
        # TODO: nice output
        max_len = max(*[len(command_id) for command_id in app["commands"].keys()])
        for command_id, info in sorted(app["commands"].items()):
            label = info.get("label", info.get("caption", ""))
            print(f"{command_id:<{max_len}}", label)


class JygRunApp(_AsyncApp):
    """Run jupyter app commands."""

    command_id: str = T.Unicode(help="the command to run").tag(config=True)
    command_args: Dict[str, Any] = T.Dict().tag(config=False)

    def parse_command_line(self, argv=None):
        """Parse extra args."""
        super().parse_command_line(argv)
        if self.extra_args:
            self.command_id = self.extra_args[0]
            self.command_args = parse_command_args(self.extra_args[1:])

    async def start_async(self):
        """Run a command."""
        if not self.command_id:
            self.log.error("need a command id")
            self.exit(1)
        bits = "commands", self.command_id
        response = await self.jyg_request(
            *bits, method="POST", body=json_encode(self.command_args)
        )
        print(response)


class JygApp(_BaseApp):
    """Work with jupyter apps from the command line."""

    subcommands = {
        k: (
            v,
            (v.__doc__ or v.__name__.replace("Jyg", "").replace("App", ""))
            .splitlines()[0]
            .strip(),
        )
        for k, v in dict(
            list=JygListApp, ls=JygListApp, l=JygListApp, run=JygRunApp, r=JygRunApp
        ).items()
    }


main = JygApp.launch_instance


if __name__ == "__main__":
    main()
