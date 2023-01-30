"""Schema for jyg."""
import json
from pathlib import Path

HERE = Path(__file__).parent

MSG_V0 = json.loads((HERE / "jyg-msg.v0.schema.json").read_text(encoding="utf-8"))
