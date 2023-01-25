"""Clean up after jsonschema-gentypes."""
import sys
from pathlib import Path

SKIP_LINES_START = [
    "    #: required",
    "    #: WARNING",
    "    #: see",
    "    #: See",
    '"""',
]
SKIP_LINE_FULL = [
    "#:",
]


def post(path: Path, title) -> int:
    """Replace boring lines."""
    new_lines = [f'''"""{title}"""''']
    for line in path.read_text(encoding="utf-8").splitlines():
        if any(line.startswith(p) for p in SKIP_LINES_START):
            continue
        if any(line.strip() == p for p in SKIP_LINE_FULL):
            continue
        new_lines += [line]

    path.write_text("\n".join(new_lines), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(post(Path(sys.argv[1]), sys.argv[2]))
