"""A safe arithmetic tool. It parses the expression with `ast` and only allows
numbers and math operators, so it can never run arbitrary code (no eval)."""
import ast
import operator
from ..tool import Tool

_BINARY = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
}
_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _eval(node):
    if isinstance(node, ast.Expression):
        return _eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY:
        return _BINARY[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY:
        return _UNARY[type(node.op)](_eval(node.operand))
    raise ValueError("only numbers and basic operators are allowed")


def calculate(expression: str) -> str:
    try:
        value = _eval(ast.parse(expression, mode="eval"))
        if isinstance(value, float) and value.is_integer():
            value = int(value)
        return str(value)
    except Exception as e:  # noqa: BLE001 - report any parse/eval issue back to the agent
        return f"Error: {e}"


CALCULATOR = Tool(
    name="calculator",
    description="Evaluate a basic arithmetic expression, e.g. '2 + 3 * 4'.",
    parameters={
        "type": "object",
        "properties": {"expression": {"type": "string", "description": "the arithmetic expression"}},
        "required": ["expression"],
    },
    func=calculate,
)
