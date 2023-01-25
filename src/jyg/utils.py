"""Utilities for jyg."""
import json
from typing import Any, Dict, List, Optional


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
