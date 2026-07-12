"""A file-reading tool, confined to a base directory.

Giving an agent the ability to read files is useful and also risky: a crafted
path like '../../secrets.env' could escape the working directory. This tool
resolves the real path and refuses anything that lands outside the allowed
base, so path traversal cannot leak files the agent was never meant to see.
"""
import os

from ..tool import Tool

MAX_BYTES = 1_000_000   # never open a file larger than this
DEFAULT_MAX_CHARS = 4000  # how much text to hand back to the model


def read_file(path: str, max_chars: int = DEFAULT_MAX_CHARS, base_dir: str = None) -> str:
    base = os.path.realpath(base_dir or os.getcwd())
    target = os.path.realpath(os.path.join(base, path))

    # Confine every read to the base directory (blocks '..' and absolute escapes).
    try:
        if os.path.commonpath([base, target]) != base:
            return "Error: path escapes the allowed directory"
    except ValueError:
        # Different drives on Windows -> definitely outside the base.
        return "Error: path escapes the allowed directory"

    if not os.path.exists(target):
        return f"Error: no such file: {path}"
    if os.path.isdir(target):
        return f"Error: {path} is a directory, not a file"
    if os.path.getsize(target) > MAX_BYTES:
        return f"Error: {path} is too large to read (over {MAX_BYTES} bytes)"

    with open(target, "r", encoding="utf-8", errors="replace") as fh:
        text = fh.read(max_chars + 1)

    if len(text) > max_chars:
        return text[:max_chars].rstrip() + f"\n... [truncated at {max_chars} characters]"
    return text


READ_FILE = Tool(
    name="read_file",
    description="Read a UTF-8 text file from the working directory and return its contents.",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "path to the file, relative to the working directory"},
            "max_chars": {"type": "integer", "description": "maximum characters to return (default 4000)"},
        },
        "required": ["path"],
    },
    func=read_file,
)
