"""The tool/skill abstraction: a Tool wraps a Python function with a name, a
description, and a JSON-schema for its arguments, so an LLM can decide to call it.
"""
from dataclasses import dataclass
from typing import Callable, Dict, Any, List


@dataclass
class Tool:
    name: str
    description: str
    parameters: Dict[str, Any]  # JSON schema for the arguments
    func: Callable[..., Any]

    def run(self, **kwargs) -> str:
        return str(self.func(**kwargs))

    def to_openai_schema(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get(self, name: str) -> Tool:
        return self._tools.get(name)

    def all(self) -> List[Tool]:
        return list(self._tools.values())

    def schemas(self) -> List[Dict[str, Any]]:
        return [t.to_openai_schema() for t in self.all()]

    def __len__(self) -> int:
        return len(self._tools)
