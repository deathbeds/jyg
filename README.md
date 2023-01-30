# `jyg`

> run Jupyter browser client commands from a CLI, REST API, or other browser windows

## Installation

> Note: after installing the browser and server extension, you'll need to **restart**
> your server and/or **refresh** your Jupyter client browser session.

### Prerequisites

- python >=3.8
- jupyterlab >=3

### `pip`

> > TBD
> >
> > ```bash
> > pip install jyg
> > ```

### `mamba`

> TBD
>
> > ```bash
> > conda install -c conda-forge jyg
> > ```

### Development Install

See the [contributing guide] for a development install.

## Quick Start

Before running any of the above, please ensure you have [installed](#installation)

### Browser

- In _Advanced Settings: Command Boards_
  - Create a new Board with a `template` like
    ```html
    <button data-command-id="help:licenses">Show Licenses</button>
    ```
  - or more complicated
    ```html
    <button
      data-command-id="apputils:change-theme"
      data-command-args='{"theme": "JupyterLab Dark"}'
    >
      Set theme
    </button>
    ```
- Click the _Launcher Item_ for the board
- Click the elements in the board

### CLI

#### List commands

```bash
jyg list --json
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
