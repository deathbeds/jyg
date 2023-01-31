"""Command line apps for jyg."""
import json
import urllib.request
from typing import Any, Dict, List, Optional, cast

import jinja2 as J
import traitlets as T
from jupyter_core.application import JupyterApp

from ._version import __version__
from .schema import msg_v0 as M
from .utils import parse_command_args


class _BaseApp(JupyterApp):
    """A base app for jyg."""

    version = __version__

    name: str = T.Unicode("jyg").tag(config=False)
    description: str = T.Unicode("a jyg application").tag(config=False)


class _APIApp(_BaseApp):
    """An app that uses the jyg REST API."""

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

    def start(self) -> None:
        """Start the request activities."""
        report = self.report_json()

        if self.mimetype not in self.mime_templates:  # pragma: no cover
            raise NotImplementedError(self.mimetype)

        tmpl = J.Template(self.mime_templates[self.mimetype])
        # TODO: async?
        result = tmpl.render(report=report, _=self, dumps=json.dumps)
        print(result)

    def report_json(self) -> Any:
        raise NotImplementedError()

    @T.default("running_servers")
    def _default_running_servers(self) -> List[Dict[str, Any]]:
        """Get running jupyter servers.

        Try to use the jupyter_server implementation if available.
        """
        running_servers: List[Dict[str, Any]] = []

        try:
            from jupyter_server import serverapp

            running_servers += [*serverapp.list_running_servers()]
        except:
            pass

        try:
            from notebook import notebookapp

            running_servers += [*notebookapp.list_running_servers()]
        except:
            pass

        if not running_servers:
            from .utils import fallback_list_running_servers

            running_servers += [*fallback_list_running_servers()]

        return running_servers

    def jyg_url(self, *bits: str) -> str:
        """Get the jyg API URL."""
        from jupyter_server.utils import url_path_join as ujoin

        # TODO: handle multiple servers
        server = self.running_servers[0]
        url = ujoin(server["url"], "jyg", *bits) + f"""?token={server["token"]}"""
        return f"{url}"

    def jyg_request(self, *bits: str, **request_kwargs: Any) -> M.AnyResponse:
        """Make a jyg request."""
        url = self.jyg_url(*bits)
        request = urllib.request.Request(url, **request_kwargs)
        response = urllib.request.urlopen(request)
        return cast(M.AnyResponse, json.load(response))


class JygListApp(_APIApp):
    """List jupyter app commands."""

    def report_json(self) -> Any:
        """Fetch the app info from a running jupyter app."""
        return self.jyg_request("commands")

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


class JygRunApp(_APIApp):
    """Run jupyter app commands."""

    command_id: str = T.Unicode(help="the command to run").tag(config=True)
    command_args: Dict[str, Any] = T.Dict().tag(config=False)

    def parse_command_line(self, argv: Optional[List[str]] = None) -> None:
        """Parse extra args as Jupyter command arguments."""
        super().parse_command_line(argv)
        if self.extra_args:
            self.command_id = self.extra_args[0]
            self.command_args = parse_command_args(self.extra_args[1:])

    def report_json(self) -> M.AnyResponse:
        """Run a command."""
        if not self.command_id:
            self.log.error("need a command id")
            self.exit(1)
        bits = "commands", self.command_id
        return self.jyg_request(
            *bits,
            method="POST",
            headers={"Content-Type": "application/json; charset=utf-8"},
            data=json.dumps(self.command_args).encode("utf-8"),
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
