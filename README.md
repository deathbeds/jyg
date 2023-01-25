# `jyg`

> remote commands for JupyterLab

## Installation

### Prerequisites

- python >=3.8
- jupyterlab >=3

### `pip`

> TBD
>
> ```bash
> pip install jyg
> ```

### Development Install

See the [contributing guide] for a development install.

## Usage

### CLI

#### List commands

```bash
jyg list
jyg ls
jyg l
```

#### Run commands

> the following are all equivalent

```bash
jyg run filebrowser:open '{"path": "Untitled.ipynb"}'
jyg run filebrowser:open --path=Untitled.ipynb
jyg r filebrowser:open --path Untitled.ipynb
```

### REST API

#### List commands

```
GET http://localhost:8888/jyg/commands

  {
    "apps": [
      {
        "url": "http://localhost:8888"
      }
    ]
  }
```

#### Run a command

```
POST http://localhost:8888/jyg/command/docmanager:open

  {
    "path": "Untitled.ipynb"
  }
```

[contributing guide]: https://github.com/deathbeds/jyg/tree/main/README.md
