"""A clock tool: returns the current UTC date and time."""
from datetime import datetime, timezone
from ..tool import Tool


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


CLOCK = Tool(
    name="clock",
    description="Return the current UTC date and time.",
    parameters={"type": "object", "properties": {}},
    func=now,
)
