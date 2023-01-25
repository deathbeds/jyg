"""Tests for the jyg argument parser."""
import json
from typing import Any, Dict, List, Tuple

import hypothesis as H
import pytest
from hypothesis import strategies as S

from jyg.utils import parse_command_args

a_value = S.deferred(
    lambda: (
        S.text(min_size=1, max_size=100)
        | S.integers(min_value=-9999, max_value=9999)
        | S.floats(min_value=-9999, max_value=9999)
        | S.booleans()
    )
)
a_path = S.deferred(lambda: S.lists(S.text(min_size=1), min_size=1))
a_kind = S.sampled_from(["flag", "eq", "split"])


@S.composite
def a_command_args_and_argv(draw: S.DrawFn) -> Tuple[Dict[str, Any], List[str]]:
    """Provide a dictionary of python args and an argv."""
    args: Dict[str, Any] = {}
    argv: List[str] = []
    num_args = draw(S.integers(min_value=1, max_value=10))
    for i in range(num_args):
        kind = draw(a_kind, label="a kind of arg")
        path = draw(a_path, label="a path")
        nest = args
        val: Any = None
        # clobbering not our problem
        if len(path) == 1:
            H.assume(path[0] not in args)

        # update args recursively
        for p in path[:-1]:
            H.assume(isinstance(nest, dict))
            if not p in nest:
                nest[p] = {}
            nest = nest[p]
        H.assume(all("/" not in p for p in path))
        # mangle the name
        name = f"--{path[0]}" if len(path) == 1 else f"""--/{"/".join(path)}"""
        H.assume("=" not in name)
        # flags are special
        if kind == "flag":
            val = True
        else:
            val = draw(a_value, label="a value")
        # the args are right now
        H.assume(isinstance(nest, dict))
        try:
            nest[path[-1]] = json.loads(val)
        except Exception:
            nest[path[-1]] = val

        # encode the args as argv
        if isinstance(val, bool):
            val = str(val).lower()
        if kind == "flag":
            argv += [name]
        elif kind == "eq":
            argv += [f"{name}={val}"]
        else:
            val = str(val)
            H.assume(not val.startswith("--"))
            argv += [name, str(val)]
    if draw(S.booleans()):
        argv = [json.dumps(args)]
    return args, argv


@pytest.mark.parametrize(
    "argv, match",
    [
        [["foo"], "Expected param"],
        [["--foo=1", "--/foo/bar"], "Can't update"],
        [["--/foo/bar=1", "--/foo/bar/baz"], "Can't update"],
    ],
)
def test_bad_args(argv: List[str], match: str) -> None:
    """Verify bad args are caught."""
    with pytest.raises(ValueError, match=match):
        parse_command_args(argv)


@H.settings(
    suppress_health_check=[H.HealthCheck.too_slow],
    # verbosity=H.Verbosity.verbose
)
@H.given(S.data())
def test_hypothesis_parse_command_args(data: Any) -> None:
    """Verify the args are parsed in a useful way."""
    expected, argv = data.draw(a_command_args_and_argv(), label="command args and argv")
    observed = parse_command_args(argv)
    assert observed == expected
