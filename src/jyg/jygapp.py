"""Command line apps for jyg."""
import asyncio
import json
from typing import Any, Dict, List, Optional, cast

import jinja2 as J
import traitlets as T
from jupyter_core.application import JupyterApp
from tornado import httpclient
from tornado.escape import json_decode, json_encode

from ._version import __version__
from .schema import msg_v0 as M
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
    mimetype: Any = T.Unicode("text/plain").tag(config=True)
    mime_templates: Any = T.Dict().tag(config=True)

    flags = {
        **_BaseApp.flags,
        "json": (
            {"_AsyncApp": {"mimetype": "application/json"}},
            "output json",
        ),
    }
    aliases = {
        **_BaseApp.aliases,
        "mime": "_AsyncApp.mimetype",
    }

    @T.default("mime_templates")
    def _default_mime_templates(self) -> Dict[str, str]:
        """Build some basic output template patterns."""
        return {
            "text/plain": "{{ dumps(report, indent=2, sort_keys=True) }}",
            "application/json": "{{ dumps(report, sort_keys=True)  }}",
        }

    @T.default("_client")
    def _default_client(self) -> httpclient.AsyncHTTPClient:
        """Get an asynchronous HTTP client."""
        return httpclient.AsyncHTTPClient()

    async def start_async(self) -> None:
        """Start the asynchronous activities."""
        report = await self.report_json()

        if self.mimetype not in self.mime_templates:  # pragma: no cover
            raise NotImplementedError(self.mimetype)

        tmpl = J.Template(self.mime_templates[self.mimetype])
        # TODO: async?
        result = tmpl.render(report=report, _=self, dumps=json.dumps)
        print(result)

    async def report_json(self) -> Any:
        raise NotImplementedError()

    @T.default("running_servers")
    def _default_running_servers(self) -> List[Dict[str, Any]]:
        """Get running jupyter servers."""
        from jupyter_server.serverapp import list_running_servers

        return [*list_running_servers()]

    def jyg_url(self, *bits: str) -> str:
        """Get the jyg API URL."""
        from jupyter_server.utils import url_path_join as ujoin

        # TODO: handle multiple servers
        server = self.running_servers[0]
        url = ujoin(server["url"], "jyg", *bits) + f"""?token={server["token"]}"""
        return f"{url}"

    async def jyg_request(self, *bits: str, **fetch_kwargs: Any) -> M.AnyResponse:
        """Make a jyg request."""
        url = self.jyg_url(*bits)
        response = await self._client.fetch(url, **fetch_kwargs)
        # TODO: use header
        return cast(M.AnyResponse, json_decode(response.body))

    def start(self) -> None:
        """Start the loop and run the start_async method."""
        asyncio.get_event_loop().run_until_complete(self.start_async())


class JygListApp(_AsyncApp):
    """List jupyter app commands."""

    async def report_json(self) -> Any:
        """Fetch the app info from a running jupyter app."""
        return await self.jyg_request("commands")

    @T.default("mime_templates")
    def _default_mime_templates(self) -> Any:
        mime_templates = dict(**super()._default_mime_templates())

        mime_templates.update(
            {
                "text/plain": """
            {%- set id_lens = [] %}
            {%- for id in report.apps[0].commands -%}
                {{ id_lens.append(id | count) or "" }}{%- endfor -%}
            {%- set max_len =  id_lens | max -%}
            {%- for id, cmd in report.apps[0].commands.items() | sort -%}
               {{- "\n" + id }}{{ (max_len - (id | count)) * " " }}\t{{ cmd.label }}
            {%- endfor %}
            """,
            }
        )
        return mime_templates


class JygRunApp(_AsyncApp):
    """Run jupyter app commands."""

    command_id: str = T.Unicode(help="the command to run").tag(config=True)
    command_args: Dict[str, Any] = T.Dict().tag(config=False)

    def parse_command_line(self, argv: Optional[List[str]] = None) -> None:
        """Parse extra args as Jupyter command arguments."""
        super().parse_command_line(argv)
        if self.extra_args:
            self.command_id = self.extra_args[0]
            self.command_args = parse_command_args(self.extra_args[1:])

    async def report_json(self) -> M.AnyResponse:
        """Run a command."""
        if not self.command_id:
            self.log.error("need a command id")
            self.exit(1)
        bits = "commands", self.command_id
        return await self.jyg_request(
            *bits, method="POST", body=json_encode(self.command_args)
        )

    @T.default("mime_templates")
    def _default_mime_templates(self) -> Any:
        mime_templates = dict(**super()._default_mime_templates())

        mime_templates.update(
            {
                "text/plain": """
            {%- if report.response.error %}ERROR: {{ report.response.error -}}
            {%- else %}OK{% endif -%}
            """,
            }
        )
        return mime_templates


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
