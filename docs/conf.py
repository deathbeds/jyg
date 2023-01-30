"""Documentation for jyg."""
import datetime
import json
import os
import re
from pathlib import Path
from typing import Any

import tomli
from sphinx.application import Sphinx

os.environ.update(IN_SPHINX="1")

CONF_PY = Path(__file__)
HERE = CONF_PY.parent
ROOT = HERE.parent
PYPROJ = ROOT / "pyproject.toml"
PROJ_DATA = tomli.loads(PYPROJ.read_text(encoding="utf-8"))
RTD = json.loads(os.environ.get("READTHEDOCS", "False").lower())

# metadata
author = PROJ_DATA["project"]["authors"][0]["name"]
project = PROJ_DATA["project"]["name"]
copyright = f"{datetime.date.today().year}, {author}"

# The full version, including alpha/beta/rc tags
release = PROJ_DATA["project"]["version"]

# The short X.Y version
version = ".".join(release.rsplit(".", 1))

# sphinx config
extensions = [
    "sphinx.ext.autosectionlabel",
    "myst_nb",
    "sphinx_copybutton",
    "sphinx-jsonschema",
]

autosectionlabel_prefix_document = True
myst_heading_anchors = 3
suppress_warnings = ["autosectionlabel.*"]

# files
# rely on the order of these to patch json, labextensions correctly
html_static_path = [
    # docs stuff
    "_static",
    # as-built application
    "../build/lite",
]
html_css_files = [
    "theme.css",
]

exclude_patterns = [
    "_build",
    ".ipynb_checkpoints",
    "**/~.*",
    "**/node_modules",
    "jupyter_execute",
    ".jupyter_cache",
    "test/",
    "tsconfig.*",
    "webpack.config.*",
]

# theme
html_theme = "pydata_sphinx_theme"
html_favicon = "_static/logo.svg"
html_logo = "_static/logo.svg"
html_theme_options = {
    "github_url": PROJ_DATA["project"]["urls"]["Source"],
    "use_edit_page_button": True,
    "header_links_before_dropdown": 10,
    "icon_links": [
        {
            "name": "PyPI",
            "url": "https://pypi.org/project/jyg",
            "icon": "fa-brands fa-python",
        },
        {
            "name": "conda-forge",
            "url": "https://github.com/conda-forge/jyg-feedstock#about-jyg",
            "icon": "_static/anvil.svg",
            "type": "local",
        },
        {
            "name": "npm",
            "url": "https://www.npmjs.com/package/@deathbeds/jyg",
            "icon": "fa-brands fa-npm",
        },
    ],
}

html_context = {
    "github_user": "deathbeds",
    "github_repo": "jyg",
    "github_version": "main",
    "doc_path": "docs",
}


def patch_jsonschema() -> None:
    """Apply some fixes to jsonschema tables."""
    WideFormat = __import__("sphinx-jsonschema").wide_format.WideFormat

    _old_transform = WideFormat.transform

    def transform_add_class(self, schema):
        table, definitions = _old_transform(self, schema)
        table.attributes["classes"] += ["jsonschema"]
        return table, definitions

    WideFormat.transform = transform_add_class


def patch_schema_anchors(app: Sphinx, exception: Any) -> None:
    """Remove known duplicate anchors."""
    if exception or "html" not in app.builder.name:
        return

    schema_out = Path(app.builder.outdir) / "schema"

    for schema_html in schema_out.glob("*.html"):
        if schema_html.name == "index.html":
            continue
        old_text = schema_html.read_text(encoding="utf-8")
        schema_html.write_text(
            re.sub(r'<span id="(.*)"></span>', "", old_text), encoding="utf-8"
        )


def setup(app):
    """Perform lite build if not already done."""
    patch_jsonschema()
    app.connect("build-finished", patch_schema_anchors)
