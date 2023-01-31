# `jyg`

|            demo             |            docs             |                                                            install                                                             |                build                 |
| :-------------------------: | :-------------------------: | :----------------------------------------------------------------------------------------------------------------------------: | :----------------------------------: |
| [![binder-badge][]][binder] | [![docs][docs-badge]][docs] | [![install from pypi][pypi-badge]][pypi] [![install from conda-forge][conda-badge]][conda] [![reuse from npm][npm-badge]][npm] | [![build][workflow-badge]][workflow] |

> run Jupyter browser client commands from a CLI, REST API, or other browser windows

[binder-badge]: https://mybinder.org/badge_logo.svg
[binder]: https://mybinder.org/v2/gh/deathbeds/jyg/HEAD?urlpath=lab
[docs-badge]: https://readthedocs.org/projects/jyg/badge/?version=latest
[docs]: https://jyg.rtfd.io
[conda-badge]: https://img.shields.io/conda/vn/conda-forge/jyg
[conda]: https://anaconda.org/conda-forge/jyg
[pypi-badge]: https://img.shields.io/pypi/v/jyg
[pypi]: https://pypi.org/project/jyg
[npm]: https://npmjs.com/package/@deathbeds/jyg
[npm-badge]: https://img.shields.io/npm/v/@deathbeds/jyg
[workflow-badge]:
  https://github.com/deathbeds/jyg/actions/workflows/ci.yml/badge.svg?branch=main
[workflow]:
  https://github.com/deathbeds/jyg/actions/workflows/ci.yml?query=branch%3Amain

See the full [documentation on ReadTheDocs](https://jyg.rtfd.io).

## Installation

> Note: after installing the browser and server extension, you'll need to **restart**
> your server and/or **refresh** your Jupyter client browser session.

### Prerequisites

- python >=3.8
- jupyterlab >=3

### `pip`

```bash
pip install jyg jupyterlab
```

### `mamba`

```bash
mamba install -c conda-forge jyg jupyterlab
```

... or use `conda` if you _must_.

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
jupyter serverextension list
```

> _You should see some output that includes:_
>
> ```
> jyg enabled
>   - Validating jyg...
>     jyg x.x.x OK
> ```

If not present, you might be able to re-enable it with:

```bash
jupyter server extension enable --sys-prefix --py jyg
jupyter serverextension enable --sys-prefix --py jyg.serverextension
```

```bash
jupyter labextension list
```

> _You should see something like:_
>
> ```
> @deathbeds/jyg vx.x.x enabled OK
> ```

### Verify the server is running

Make sure the server is running.

```bash
jupyter server list
jupyter notebook list
```

### Verify the browser application is running

To run or list commands, the browser must be running the client. Also look at the
_Browser Console_ (usually shown with <kbd>f12</kbd>) for any explicit errors or
warnings.

## Frequently Asked Questions

### Does `jyg` work with Jupyter `notebook<7`?

**Sort of.** `jyg` can list and run commands in JupyterLab-derived apps running as an
extension to the `notebook` server... but only when running under `jupyter_server<2`.

It cannot (and will not) integrate with the Bootstrap/jQuery notebook UI, as there is
consistent design pattern for commands.

### Does `jyg` work with Jupyter `notebook>=7`?

**Not yet.** But it will probably work pretty soon after a release.

### Does `jyg` work with another backend than `jupyter_server`?

**No.** Aside from the above about `notebook<7`. However, the API is extensively typed
and tested, and could be implemented in another backend.

### Can `$MY_APPLICATION` use `jyg` to drive Jupyter clients?

**Probably not.** Out of the box. `jyg` only provides a way to operate its host
application in co-deployed `<iframe>`s as _Command Boards_, and only runs the
`postMessage` server when a board is actively running.

The in-browser API is available, however, to create custom extensions which would allow
a web page that _already_ had access to the Jupyter application to register use
`postMessage`.

If your application _already_ has control over the Jupyter application, you can likely
use a handle to the `Application` instance, get access to the `IWindowProxy` plugin, and
add the host window as a source.
