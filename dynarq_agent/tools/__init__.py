"""Built-in tools and the default registry."""
from ..tool import ToolRegistry
from .calculator import CALCULATOR
from .datetime_tool import CLOCK
from .text_tools import TEXT_STATS
from .converter import CONVERTER

BUILTINS = [CALCULATOR, CLOCK, TEXT_STATS, CONVERTER]


def default_registry() -> ToolRegistry:
    registry = ToolRegistry()
    for tool in BUILTINS:
        registry.register(tool)
    return registry
