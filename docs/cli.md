# CLI

The `jyg` CLI is built on [`jupyter_core`][jupyter-core], so it can be launched in a
number of ways:

```bash
jupyter jyg
jyg
python -m jyg
```

[jupyter-core]: https://github.com/jupyter/jupyter_core

## Subcommands

### List commands

```bash
jyg list  # or `ls` or `l`
```

### Run command

```bash
jupyter jyg run filebrowser:open '{"path": "Untitled.ipynb"}'
jyg run filebrowser:open --path=Untitled.ipynb
jyg r filebrowser:open --path Untitled.ipynb
```

## Common arguments

## `--format`

Modify the report format. Currently only `text/plain` and `application/json` are
implemented.

## `--json`

A shortcut for `--format application/json`
