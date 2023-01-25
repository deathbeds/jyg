"""Tests for the jyg CLI."""
import sys
from typing import List

import pytest

from jyg import __version__

from .conftest import WIN, TScriptRunner

ARGVS = [
    ["jupyter", "jyg"],
    ["jupyter-jyg"],
    ["jyg"],
    [sys.executable, "-m", "jyg"],
]
LISTS = [
    ["list"],
    ["ls"],
    ["l"],
]


@pytest.mark.parametrize("argv", ARGVS)
def test_cli_version(script_runner: TScriptRunner, argv: List[str]) -> None:
    """Verify invoking the CLI returns the version."""
    ret = script_runner.run(*argv, "--version")
    assert ret.success
    if WIN:  # pragma: no cover
        return
    assert __version__ in ret.stdout
