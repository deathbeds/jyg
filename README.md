# `jyg`

> run Jupyter browser client commands from a CLI, REST API, or other browser windows

See the full [documentation on ReadTheDocs](https://jyg.rtfd.io).

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
> > pip install jyg jupyterlab
> > ```

### `mamba`

> TBD
>
> > ```bash
> > mamba install -c conda-forge jyg jupyterlab python >=3.8
> > ```
>
> ... or use `conda` if you _must_.

### Development Install

See the [contributing guide] for a development install.

[contributing guide]: https://github.com/deathbeds/jyg/tree/main/README.md

## Quick Start

Before running any of the above, please ensure you have [installed](#installation) the
`jyg` extension for your Jupyter client and server.

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
  - Or use the _Command Palette_
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

## Troubleshooting

If various pieces do not appear to be working, try some of the steps below.

### Verify the installation

```bash
jupyter server extension list
```

> _You should see some output that includes:_
>
> ```
> jyg enabled
>   - Validating jyg...
>     jyg x.x.x OK
> ```

```bash
jupyter labextension list
```

> _You should see something like:_
>
> ```
> @deathbeds/jyg v0.1.0 enabled OK
> ```

### The server is running

Make sure the server is running.

```bash
jupyter server list
```

### The application is running

To run or list commands, the browser must be running the client. Also look at the
_Browser Console_ (usually shown with <kbd>f12</kbd>) for any explicit errors or
warnings.

## Frequently Asked Questions

### Does `jyg` work with Jupyter `notebook <7`?

No. And it won't.

### Does `jyg` work with Jupyter `notebook >=7`?

Not yet.

### Does `jyg` work with another backend than `jupyter_server`?

No. However, the API is relatively straightforward.

### Can `$MY_APPLICATION` use `jyg` to drive Jupyter clients?

Probably not. `jyg` only provides a way to operate its host application in co-deployed
`<iframe>` (Command Boards).

The API is available, however, to create custom extensions which would allow a web page
that _already_ had access to the Jupyter application to register use `postMessage`.
