# API

When installed as a server extension, a few endpoints are available for interacting with
the `jyg` API.

```{hint}
This also powers the [CLI](./cli.md).
```

## `/jyg/commands`

> List all known apps and their commands

```
GET http://localhost:8888/jyg/commands
```

This will return something like this, but with a _lot_ more `commands` and `plugins`:

```json
{
  "apps": [
    {
      "commands": {
        "help:licenses": { "isEnabled": true, "isVisible": true, "label": "Licenses" }
      },
      "name": "JupyterLab",
      "plugins": ["@deathbeds/jyg:plugin"],
      "title": "lab - JupyterLab",
      "url": "http://127.0.0.1:8888/lab",
      "version": "3.5.3"
    }
  ]
}
```

The keys of the `commands` member can be used to run commands, described below.

## `/jyg/commands/{:command-id}`

> Run a command

```
POST http://localhost:8888/jyg/commands/help:licenses
```

```{hint}
For commands that block, like `notebook:restart-run-all`, the command will
wait until an in-browser confirmation has occurred.
```
