"""Suite-level test configuration for jyg."""
import os
import platform
from pathlib import Path
from typing import Callable, Iterator
from unittest import mock

import pytest

pytest_plugins = [
    "hypothesispytest",
]

WIN = platform.system() == "Windows"


class TScriptResult:
    """A type for script_runner results."""

    success: bool
    stdout: str
    stderr: str
    returncode: int


class TScriptRunner:
    """A type for script_runner."""

    run: Callable[..., TScriptResult]


@pytest.fixture
def tmp_home(tmp_path: Path) -> Iterator[Path]:
    """Run a test in an empty home dir."""
    home = tmp_path / "__home__"
    with mock.patch.dict(os.environ, {"HOME": str(home)}):
        yield home
