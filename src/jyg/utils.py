"""Utilities for jyg."""
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional


def is_pid_killable(pid: int) -> bool:
    """Abuse ``os.kill`` to check whether a process is running.

    This can _still_ report a process is running if it has zombie
    kernels, etc.
    """
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def fallback_list_running_servers() -> Iterator[Dict[str, Any]]:
    """Iterate over the server info files of running Jupyter/notebook servers.

    Given a runtime directory, find (nb|jp)server-* files in the security directory,
    and yield dicts of their information, each one pertaining to a currently
    running Jupyter server instance.

    Adapted from:

    https://github.com/jupyter-server/jupyter_server/blob/v2.1.0/jupyter_server/serverapp.py#L2922
    """
    from jupyter_core.paths import jupyter_runtime_dir

    runtime_dir = Path(jupyter_runtime_dir())

    # find info paths in time order order
    info_paths = sorted(
        [
            *runtime_dir.glob("jpserver-*.json"),
            *runtime_dir.glob("nbserver-*.json"),
        ],
        key=lambda s: s.stat().st_mtime,
    )

    for info_path in reversed(info_paths):
        try:
            with info_path.open() as fd:
                info = json.load(fd)
        except Exception:
            continue
        if "pid" in info and is_pid_killable(info["pid"]):
            yield info


def parse_command_args(argv: List[str]) -> Dict[str, Any]:
    """Parse shell-style tokens to arbitrary JSON."""
    args: Dict[str, Any] = {}

    if len(argv) == 1 and argv[0].startswith("{") and argv[0].endswith("}"):
        try:
            args = json.loads(argv[0])
            return args
        except Exception:  # pragma: no cover
            pass
    else:
        num_args = len(argv)
        i = 0
        while i < num_args:
            arg = argv[i]
            arg_name: Optional[str] = None
            arg_value: Any = None

            if not arg.startswith("--"):
                raise ValueError(f"Expected param: maybe --{arg} instead of {arg}")

            if "=" in arg:
                arg_name, arg_value = arg.split("=", 1)
            elif i + 1 == num_args:
                arg_name = arg
                arg_value = True
            elif i < num_args:
                if argv[i + 1].startswith("--"):
                    arg_name = arg
                    arg_value = True
                else:
                    arg_name = arg
                    arg_value = argv[i + 1]
                    i += 1
            else:
                arg_name = arg
                arg_value = True

            i += 1

            try:
                arg_value = json.loads(arg_value)
            except:
                pass

            if arg_name.startswith("--/"):
                nest = args
                arg_bits = arg_name.split("/")[1:]
                for bit in arg_bits[:-1]:
                    if not isinstance(nest, dict):
                        msg = f"""Can't update /{"/".join(arg_bits)} from {arg_name} in {args}"""
                        raise ValueError(msg)
                    if not bit in nest:
                        nest[bit] = {}
                    nest = nest[bit]
                if not isinstance(nest, dict):
                    msg = f"""Can't update /{"/".join(arg_bits)} from {arg_name} in {args}"""
                    raise ValueError(msg)
                nest[arg_bits[-1]] = arg_value
            else:
                args[arg_name[2:]] = arg_value

    return args
