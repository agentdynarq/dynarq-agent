"""A text statistics tool: counts words, characters and sentences."""
import re
from ..tool import Tool


def text_stats(text: str) -> str:
    words = len(re.findall(r"\b\w+\b", text))
    chars = len(text)
    sentences = len([s for s in re.split(r"[.!?]+", text) if s.strip()])
    return f"{words} words, {chars} characters, {sentences} sentence(s)"


TEXT_STATS = Tool(
    name="text_stats",
    description="Count the words, characters and sentences in a piece of text.",
    parameters={
        "type": "object",
        "properties": {"text": {"type": "string", "description": "the text to analyse"}},
        "required": ["text"],
    },
    func=text_stats,
)
